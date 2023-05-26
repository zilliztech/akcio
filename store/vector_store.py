import logging
from typing import Optional, Any, Tuple, List

from langchain.vectorstores import Milvus
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document

import sys
import os

sys.path.append(os.path.dirname(__file__))

from config import vectordb_config


logger = logging.getLogger('vector_store')

HOST = vectordb_config.get('host', 'localhost')
PORT = vectordb_config.get('port', 19530)
TOP_K = vectordb_config.get('top_k', 10)


class VectorStore(Milvus):
    '''
    Vector database APIs: insert, search
    '''
    def __init__(self, table_name: str, embedding_func: Embeddings):
        '''Initialize vector db'''
        assert isinstance(embedding_func, Embeddings), 'Invalid embedding function. Only accept langchain.embeddings.'
        self.embedding_func = embedding_func
        self.connect_args = {
            'host': HOST,
            'port': PORT
        }
        self.collection_name = table_name
        super().__init__(
            embedding_function=self.embedding_func,
            collection_name=self.collection_name,
            connection_args=self.connect_args,
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
        docs = self.similarity_search(
            query=query,
            k=TOP_K,
            param=''
        )
        res = []
        for doc in docs:
            if 'text' in doc.metadata:
                del doc.metadata['text']
            res.append(doc)
        return res
    
    def drop(self):
        confirm = input(f'Confirm to drop table {self.collection_name} vector db (y/n): ')
        if confirm == 'y':
            self.col.release()
            self.col.drop()
        else:
            raise RuntimeError('Exiting...')
    
    @classmethod
    def has_project(cls, project:str, host: str = HOST, port: str = PORT):
        from pymilvus import connections, utility

        connections.connect(host=host, port=port)

        return utility.has_collection(project)


    
