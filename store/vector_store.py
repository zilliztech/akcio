import logging
from typing import List

from langchain.vectorstores import Milvus
from langchain.embeddings.base import Embeddings

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
        
    def insert(self, docs: List[str]):
        '''Insert data'''
        pks = self.add_texts(
            texts=docs
        )
        return len(pks)

    def search(self, query: str):
        '''Query data'''
        res_docs = self.similarity_search(
            query=query,
            k=TOP_K
        )
        return res_docs
    
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


    
