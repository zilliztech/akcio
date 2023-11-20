import sys
import os
from typing import Any, Dict

from pymilvus import Collection, connections
from towhee import AutoConfig

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import ( # pylint: disable=C0413
    USE_SCALAR, LLM_OPTION,
    TEXTENCODER_CONFIG, CHAT_CONFIG,
    VECTORDB_CONFIG, SCALARDB_CONFIG,
    RERANK_CONFIG, QUERY_MODE, INSERT_MODE,
    DATAPARSER_CONFIG
)
from src.towhee.base import BasePipelines  # pylint: disable=C0413
from src.towhee.pipelines.search import build_search_pipeline  # pylint: disable=C0413
from src.towhee.pipelines.insert import build_insert_pipeline  # pylint: disable=C0413


class TowheePipelines(BasePipelines):
    '''Towhee pipelines'''
    def __init__(self,
                 llm_src: str = LLM_OPTION,
                 use_scalar: bool = USE_SCALAR,
                 chat_config: Dict = CHAT_CONFIG,
                 textencoder_config: Dict = TEXTENCODER_CONFIG,
                 vectordb_config: Dict = VECTORDB_CONFIG,
                 scalardb_config: Dict = SCALARDB_CONFIG,
                 rerank_config: Dict = RERANK_CONFIG,
                 query_mode: str = QUERY_MODE,
                 insert_mode: str = INSERT_MODE,
                 chunk_size: int = DATAPARSER_CONFIG['chunk_size']
                 ): # pylint: disable=W0102
        self.use_scalar = use_scalar
        self.llm_src = llm_src
        self.query_mode = query_mode
        self.insert_mode = insert_mode

        self.chat_config = chat_config
        self.textencoder_config = textencoder_config
        self.rerank_config = rerank_config
        self.chunk_size = chunk_size

        self.milvus_topk = vectordb_config.get('top_k', 5)
        self.milvus_threshold = vectordb_config.get('threshold', 0)
        self.milvus_index_params = vectordb_config.get('index_params', {})

        self.connection_args = vectordb_config['connection_args']
        for k, v in self.connection_args.copy().items():
            if v is None:
                del self.connection_args[k]
            if isinstance(v, str) and len(v) == 0:
                del self.connection_args[k]

        if 'uri' in self.connection_args:
            self.milvus_uri = self.connection_args['uri']
            self.milvus_host = self.connection_args.pop('host', None)
            self.milvus_port = self.connection_args.pop('port', None)
        elif 'host' in self.connection_args and 'port' in self.connection_args:
            self.milvus_uri = None
            self.milvus_host = self.connection_args.get('host')
            self.milvus_port = self.connection_args.get('port')
        else:
            raise AttributeError('Invalid connection args for milvus.')

        if 'token' in self.connection_args:
            self.milvus_token = self.connection_args.get('token', None)
            self.milvus_user = self.connection_args.pop('user', None)
            self.milvus_password = self.connection_args.pop('password', None)
        else:
            self.milvus_token = None
            self.milvus_user = self.connection_args.get('user')
            self.milvus_password = self.connection_args.get('password')

        if self.milvus_token or self.milvus_user:
            self.connection_args['secure'] = True
            self.milvus_secure = True

        connections.connect(**self.connection_args)

        if self.use_scalar:
            from elasticsearch import Elasticsearch  # pylint: disable=C0415

            self.es_connection_kwargs = scalardb_config['connection_args']
            self.es_top_k = scalardb_config['top_k']
            self.es_client = Elasticsearch(**self.es_connection_kwargs)

    @property
    def search_pipeline(self):
        search_pipeline = build_search_pipeline(
            self.query_mode, config=self.search_config)
        return search_pipeline

    @property
    def insert_pipeline(self):
        insert_pipeline = build_insert_pipeline(
            self.insert_mode, config=self.insert_config)
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


        # Configure vector store (Milvus/Zilliz)
        search_config.milvus_uri = self.milvus_uri
        search_config.milvus_token = self.milvus_token
        search_config.milvus_host = self.milvus_host
        search_config.milvus_port = self.milvus_port
        search_config.milvus_user = self.milvus_user
        search_config.milvus_password = self.milvus_password
        search_config.milvus_top_k = self.milvus_topk
        search_config.threshold = self.milvus_threshold

        # Configure scalar store (ES)
        if self.use_scalar:
            search_config.es_enable = True
            search_config.es_connection_kwargs = self.es_connection_kwargs
            search_config.es_top_k = self.es_top_k
        else:
            search_config.es_enable = False
        return search_config

    @property
    def insert_config(self):
        insert_config = AutoConfig.load_config(
            'osschat-insert',
            llm_src=self.llm_src,
            **self.chat_config[self.llm_src]
            )
        # Configure chunk size
        insert_config.chunk_size = self.chunk_size

        # Configure embedding
        insert_config.embedding_model = self.textencoder_config['model']
        insert_config.embedding_normalize = self.textencoder_config['norm']
        insert_config.embedding_device = self.textencoder_config['device']

        # Configure vector store (Milvus/Zilliz)
        insert_config.milvus_uri = self.milvus_uri
        insert_config.milvus_token = self.milvus_token
        insert_config.milvus_host = self.milvus_host
        insert_config.milvus_port = self.milvus_port
        insert_config.milvus_user = self.milvus_user
        insert_config.milvus_password = self.milvus_password

        # Configure scalar store (ES)
        if self.use_scalar:
            insert_config.es_enable = True
            insert_config.es_connection_kwargs = self.es_connection_kwargs
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
                        description='text', max_length=1000)
        ]
        if INSERT_MODE == 'generate_questions':
            fields.append(FieldSchema(name='question', dtype=DataType.VARCHAR,
                        description='generated question', max_length=500))
        fields.append(FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR,
                        description='embedding vectors', dim=self.textencoder_config['dim']))
        schema = CollectionSchema(fields=fields, description='osschat', enable_dynamic_field=False)
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
        if not self.check(project):
            milvus_count = es_count = None
        else:
            collection = Collection(project)
            collection.flush()
            milvus_count = collection.num_entities
            if self.use_scalar:
                es_count = self.es_client.count(index=project)['count']
            else:
                es_count = None
        return {'vector store': milvus_count, 'scalar store': es_count}
