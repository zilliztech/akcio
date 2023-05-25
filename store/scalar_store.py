from typing import Any, Iterable

import elasticsearch
from langchain.retrievers import ElasticSearchBM25Retriever

from .config import scalardb_config


class ScalarStore(ElasticSearchBM25Retriever):
    def __init__(self, index_name: str, client: Any = elasticsearch.Elasticsearch(**scalardb_config)):
        super().__init__(client=client, index_name=index_name)

    def insert(self, data: Iterable[str]):
        '''Insert data'''
        ids = self.add_texts(texts=data)
        return len(ids)

    def search(self, query: str):
        '''Query data'''
        res_docs = self.get_relevant_documents(query=query)
        return res_docs
    
    def drop(self):
        # confirm = input(f'Confirm to drop table {self.table_name} scalar db (y/n): ')
        # if confirm == 'y':
        #     self.col.release()
        #     self.col.drop()
        pass
    
    @classmethod
    def has_project(cls, project: str):
        pass