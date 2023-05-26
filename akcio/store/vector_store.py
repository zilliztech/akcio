import logging
from typing import Optional, Any, Tuple, List

from langchain.vectorstores import Milvus
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document

from .config import vectordb_config


logger = logging.getLogger('vector_store')

CONNECTION_ARGS = vectordb_config.get('connection_args', {'host': 'localhost', 'port': 19530})
TOP_K = vectordb_config.get('top_k', 10)
INDEX_PARAMS = vectordb_config.get('index_params', None)
SEARCH_PARAMS = vectordb_config.get('search_params', None)


class VectorStore(Milvus):
    '''
    Vector database APIs: insert, search
    '''

    def __init__(self, table_name: str, embedding_func: Embeddings, connection_args: dict = CONNECTION_ARGS):
        '''Initialize vector db'''
        assert isinstance(
            embedding_func, Embeddings), 'Invalid embedding function. Only accept langchain.embeddings.'
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
            raise RuntimeError("No existing collection to search.")

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

    def insert(self, data: List[str], metadatas: Optional[list[dict]] = None):
        '''Insert data'''
        pks = self.add_texts(
            texts=data,
            metadatas=metadatas
        )
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

    @classmethod
    def connect(cls, connection_args: dict = CONNECTION_ARGS):
        from pymilvus import connections  # pylint: disable=C0415

        connections.connect(**connection_args)

    @classmethod
    def drop(cls, project: str, connection_args: dict = CONNECTION_ARGS):
        if cls.has_project(project=project, connection_args=connection_args):
            from pymilvus import Collection  # pylint: disable=C0415

            collection = Collection(project)
            confirm = input(f'Confirm to drop table {project} vector db (y/n): ')
            if confirm == 'y':
                collection.release()
                collection.drop()
            else:
                raise RuntimeError('Stop dropping table ...')
        else:
            raise AttributeError(f'No table in vector db: {project}')

    @classmethod
    def has_project(cls, project: str, connection_args: dict = CONNECTION_ARGS):
        from pymilvus import utility # pylint: disable=C0415

        cls.connect(connection_args)
        return utility.has_collection(project)
