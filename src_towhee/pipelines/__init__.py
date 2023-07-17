import sys
import os
from typing import Any, Dict

from pymilvus import Collection, connections
from towhee import AutoConfig, AutoPipes

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import ( # pylint: disable=C0413
    USE_SCALAR, LLM_OPTION,
    TEXTENCODER_CONFIG, CHAT_CONFIG,
    VECTORDB_CONFIG, SCALARDB_CONFIG,
    RERANK_CONFIG
)
from src_towhee.pipelines.prompts import PROMPT_OP  # pylint: disable=C0413
from src_towhee.base import BasePipelines  # pylint: disable=C0413


class TowheePipelines(BasePipelines):
    '''Towhee pipelines'''
    def __init__(self,
                 llm_src: str = LLM_OPTION,
                 use_scalar: bool = USE_SCALAR,
                 prompt_op: Any = PROMPT_OP,
                 chat_config: Dict = CHAT_CONFIG,
                 textencoder_config: Dict = TEXTENCODER_CONFIG,
                 vectordb_config: Dict = VECTORDB_CONFIG,
                 scalardb_config: Dict = SCALARDB_CONFIG,
                 rerank_config: Dict = RERANK_CONFIG
                 ): # pylint: disable=W0102
        self.prompt_op = prompt_op
        self.use_scalar = use_scalar
        self.llm_src = llm_src

        self.chat_config = chat_config
        self.textencoder_config = textencoder_config
        self.rerank_config = rerank_config

        self.milvus_uri = vectordb_config['connection_args']['uri']
        self.milvus_host = self.milvus_uri.split('https://')[1].split(':')[0]
        self.milvus_port = self.milvus_uri.split('https://')[1].split(':')[1]
        milvus_user = vectordb_config['connection_args'].get('user')
        self.milvus_user = None if milvus_user == '' else milvus_user
        milvus_password = vectordb_config['connection_args'].get('password')
        self.milvus_password = None if milvus_password == '' else milvus_password
        self.milvus_topk = vectordb_config.get('top_k', 5)
        self.milvus_threshold = vectordb_config.get('threshold', 0)
        self.milvus_index_params = vectordb_config.get('index_params', {})

        connections.connect(
            host=self.milvus_host,
            port=self.milvus_port,
            user=self.milvus_user,
            password=self.milvus_password
        )

        if self.use_scalar:
            from elasticsearch import Elasticsearch  # pylint: disable=C0415

            self.es_uri = scalardb_config['connection_args']['hosts']
            self.es_host = self.es_uri.split('https://')[1].split(':')[0]
            self.es_port = self.es_uri.split('https://')[1].split(':')[1]
            self.es_ca_certs = scalardb_config['connection_args']['ca_certs']
            self.es_basic_auth = scalardb_config['connection_args']['basic_auth']
            self.es_user = self.es_basic_auth[0]
            self.es_password = self.es_basic_auth[1]
            self.es_client = Elasticsearch(
                self.es_uri,
                ca_certs=self.es_ca_certs,
                basic_auth=self.es_basic_auth
            )

    @property
    def search_pipeline(self):
        search_pipeline = AutoPipes.pipeline(
            'osschat-search', config=self.search_config)
        return search_pipeline

    @property
    def insert_pipeline(self):
        insert_pipeline = AutoPipes.pipeline(
            'osschat-insert', config=self.insert_config)
        return insert_pipeline

    @property
    def search_config(self):
        search_config = AutoConfig.load_config(
            'osschat-search',
            llm_src=self.llm_src,
            **self.rerank_config,
            **self.chat_config[self.llm_src]
        )

        # Configure embedding
        search_config.embedding_model = self.textencoder_config['model']
        search_config.embedding_normalize = self.textencoder_config['norm']
        search_config.embedding_device = self.textencoder_config['device']

        # Configure prompt
        if self.prompt_op:
            search_config.customize_prompt = self.prompt_op

        # Configure vector store (Milvus/Zilliz)
        search_config.milvus_host = self.milvus_host
        search_config.milvus_port = self.milvus_port
        search_config.milvus_user = self.milvus_user
        search_config.milvus_password = self.milvus_password
        search_config.milvus_top_k = self.milvus_topk
        search_config.threshold = self.milvus_threshold

        # Configure scalar store (ES)
        if self.use_scalar:
            search_config.es_enable = True
            search_config.es_host = self.es_host
            search_config.es_port = self.es_port
            search_config.es_user = self.es_user
            search_config.es_password = self.es_password
            search_config.es_ca_certs = self.es_ca_certs
        else:
            search_config.es_enable = False
        return search_config

    @property
    def insert_config(self):
        insert_config = AutoConfig.load_config('osschat-insert')

        # Configure embedding
        insert_config.embedding_model = self.textencoder_config['model']
        insert_config.embedding_normalize = self.textencoder_config['norm']
        insert_config.embedding_device = self.textencoder_config['device']

        # Configure vector store (Milvus/Zilliz)
        insert_config.milvus_host = self.milvus_host
        insert_config.milvus_port = self.milvus_port
        insert_config.milvus_user = self.milvus_user
        insert_config.milvus_password = self.milvus_password

        # Configure scalar store (ES)
        if self.use_scalar:
            insert_config.es_enable = True
            insert_config.es_host = self.es_host
            insert_config.es_port = self.es_port
            insert_config.es_user = self.es_user
            insert_config.es_password = self.es_password
            insert_config.es_ca_certs = self.es_ca_certs
        else:
            insert_config.es_enable = False
        return insert_config

    def create(self, project: str):
        from pymilvus import CollectionSchema, FieldSchema, DataType # pylint: disable=C0415

        fields = [
            FieldSchema(name='id', dtype=DataType.INT64,
                        description='ids', is_primary=True, auto_id=True),
            FieldSchema(name='text_id', dtype=DataType.VARCHAR,
                        description='text', max_length=500),
            FieldSchema(name='text', dtype=DataType.VARCHAR,
                        description='text', max_length=1000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR,
                        description='embedding vectors', dim=self.textencoder_config['dim'])
        ]
        schema = CollectionSchema(fields=fields, description='osschat')
        collection = Collection(name=project, schema=schema)

        index_params = self.milvus_index_params
        collection.create_index(field_name='embedding',
                                index_params=index_params)
        return collection

    def drop(self, project):
        assert self.check(project), f'No project store: {project}'
        # drop vector store
        collection = Collection(project)
        collection.drop()

        if self.use_scalar:
            # drop scalar store
            self.es_client.indices.delete(index=project)

        assert not self.check(
            project), f'Failed to drop project store : {project}'

    def check(self, project):
        from pymilvus import utility  # pylint: disable=C0415

        status = utility.has_collection(project)  # check vector store
        if self.use_scalar:
            assert self.es_client.indices.exists(
                index=project) == status  # check scalar store
        return status

    def count_entities(self, project):
        collection = Collection(project)
        collection.flush()
        milvus_count = collection.num_entities
        if self.use_scalar:
            es_count = self.es_client.count(index=project)['count']
            assert es_count == milvus_count, 'Mismatched data count in Milvus vs Elastic.'
        return milvus_count
