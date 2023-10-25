import os
import sys
import logging
from typing import Optional, Any, Tuple, List, Dict, Union
from uuid import uuid4

from langchain.vectorstores import Milvus
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from config import VECTORDB_CONFIG  # pylint: disable=C0413


logger = logging.getLogger('vector_store')

CONNECTION_ARGS = VECTORDB_CONFIG.get('connection_args', {'uri': 'http://localhost:19530'})
TOP_K = VECTORDB_CONFIG.get('top_k', 3)
INDEX_PARAMS = VECTORDB_CONFIG.get('index_params', None)
SEARCH_PARAMS = VECTORDB_CONFIG.get('search_params', None)


class VectorStore(Milvus):
    '''
    Vector database APIs: insert, search
    '''

    def __init__(self, table_name: str, embedding_func: Embeddings = None, connection_args: dict = CONNECTION_ARGS):
        '''Initialize vector db

        connection_args:
            uri: milvus or zilliz uri
            token: zilliz token
        '''
        # assert isinstance(
        #     embedding_func, Embeddings), 'Invalid embedding function. Only accept langchain.embeddings.'
        self.embedding_func = embedding_func
        self.connect_args = connection_args
        self.collection_name = table_name
        super().__init__(
            embedding_function=self.embedding_func,
            collection_name=self.collection_name,
            connection_args=self.connect_args,
            index_params=INDEX_PARAMS,
            search_params=SEARCH_PARAMS
        )

    def _create_connection_alias(self, connection_args: dict) -> str:
        """Create the connection to the Milvus server."""
        from pymilvus import MilvusException, connections  # pylint: disable = C0415

        # Grab the connection arguments that are used for checking existing connection
        host: str = connection_args.get('host', None)
        port: Union[str, int] = connection_args.get('port', None)
        uri: str = connection_args.get('uri', None)
        user = connection_args.get('user', None)
        password = connection_args.get('password', None)
        token = connection_args.get('token', None)


        _connection_args = {}  # pylint: disable = C0103
        # Order of use is uri > host/port
        if uri is not None:
            _connection_args['uri'] = uri
            given_address = uri.split('://')[1]
        elif host is not None and port is not None:
            _connection_args['host'] = host
            _connection_args['port'] = port
            given_address = f'{host}:{port}'
        else:
            logger.debug('Missing standard address type for reuse attempt')
            given_address = None

        # Order of use is token > user/password
        if token is not None:
            _connection_args['token'] = token
            _connection_args['secure'] = True
        elif user is not None and password is not None:
            _connection_args['user'] = user
            _connection_args['password'] = password
            _connection_args['secure'] = True
        else:
            _connection_args['secure'] = False

        # If a valid address was given, then check if a connection exists
        if given_address is not None:
            for con in connections.list_connections():
                addr = connections.get_connection_addr(con[0])
                if addr == given_address:
                    logger.debug('Using previous connection: %s', con[0])
                    return con[0]

        # Generate a new connection if one doesn't exist
        alias = uuid4().hex
        try:
            connections.connect(alias=alias, **_connection_args)
            logger.debug('Created new connection using: %s', alias)
            return alias
        except MilvusException as e:
            logger.error('Failed to create new connection using: %s', alias)
            raise e

    def similarity_search_with_score_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        if self.col is None:
            raise RuntimeError('No existing collection to search.')

        if param is None:
            param = self.search_params

        # Determine result metadata fields.
        output_fields = self.fields[:]
        output_fields.remove(self._vector_field)

        # Perform the search.
        res = self.col.search(
            data=[embedding],
            anns_field=self._vector_field,
            param=param,
            limit=k,
            expr=expr,
            output_fields=output_fields,
            timeout=timeout,
            **kwargs,
        )
        # Organize results.
        ret = []
        if 'doc' in output_fields:
            doc_field = 'doc'
        else:
            doc_field = self._text_field
        for result in res[0]:
            meta = {x: result.entity.get(x) for x in output_fields}
            doc = Document(page_content=meta.pop(doc_field), metadata=meta)
            pair = (doc, result.score)
            ret.append(pair)

        return ret

    def insert(self, data: List[str], metadatas: Optional[List[dict]] = None):
        '''Insert data'''
        pks = self.add_texts(
            texts=data,
            metadatas=metadatas
        )
        return len(pks)

    def insert_embeddings(self,
                          data: List[float],
                          metadatas: List[dict],
                          timeout: Optional[int] = None,
                          batch_size: int = 1000,
                          **kwargs: Any
                          ):
        '''Insert embeddings with texts'''
        from pymilvus import Collection, MilvusException  # pylint: disable=C0415

        embeddings = list(data)
        texts = []
        for d in metadatas:
            texts.append(d.pop('text'))

        if len(embeddings) == 0:
            logger.debug('Nothing to insert, skipping.')
            return []

        # If the collection hasnt been initialized yet, perform all steps to do so
        if not isinstance(self.col, Collection):
            self._init(embeddings, metadatas)

        # Dict to hold all insert columns
        insert_dict: Dict[str, list] = {
            self._text_field: texts,
            self._vector_field: embeddings,
        }

        # Collect the metadata into the insert dict.
        for d in metadatas:
            for key, value in d.items():
                if key in self.fields:
                    insert_dict.setdefault(key, []).append(value)

        # Total insert count
        vectors: list = insert_dict[self._vector_field]
        total_count = len(vectors)

        pks: List[str] = []

        assert isinstance(self.col, Collection)
        for i in range(0, total_count, batch_size):
            # Grab end index
            end = min(i + batch_size, total_count)
            # Convert dict to list of lists batch for insertion
            insert_list = [insert_dict[x][i:end] for x in self.fields]
            # Insert into the collection.
            try:
                res: Collection
                res = self.col.insert(insert_list, timeout=timeout, **kwargs)
                pks.extend(res.primary_keys)
            except MilvusException as e:
                logger.error(
                    'Failed to insert batch starting at entity: %s/%s', i, total_count
                )
                raise e
        return len(pks)


    def search(self, query: str) -> List[Document]:
        '''Query data'''
        assert self.col, f'No project table: {self.collection_name}'
        docs = self.similarity_search(
            query=query,
            k=TOP_K,
            param=self.search_params
        )
        res = []
        for doc in docs:
            if 'text' in doc.metadata:
                del doc.metadata['text']
            res.append(doc)
        return res

    @staticmethod
    def connect(connection_args: dict = CONNECTION_ARGS):
        from pymilvus import connections  # pylint: disable=C0415

        connections.connect(**connection_args)

    @staticmethod
    def drop(project: str, connection_args: dict = CONNECTION_ARGS):
        if VectorStore.has_project(project=project, connection_args=connection_args):
            from pymilvus import Collection  # pylint: disable=C0415

            collection = Collection(project)
            # confirm = input(f'Confirm to drop table {project} vector db (y/n): ')
            # if confirm == 'y':
            try:
                collection.release()
                collection.drop()
            except Exception as e:
                raise RuntimeError from e
        else:
            raise AttributeError(f'No table in vector db: {project}')

    @staticmethod
    def has_project(project: str, connection_args: dict = CONNECTION_ARGS):
        from pymilvus import utility # pylint: disable=C0415

        VectorStore.connect(connection_args)
        return utility.has_collection(project)


    @staticmethod
    def count_entities(project: str, connection_args: dict = CONNECTION_ARGS):
        from pymilvus import Collection # pylint: disable=C0415

        VectorStore.connect(connection_args)
        collection = Collection(project)
        return collection.num_entities
