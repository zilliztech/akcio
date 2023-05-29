from typing import Any, Iterable

import elasticsearch
from langchain.retrievers import ElasticSearchBM25Retriever

from ..config import scalardb_config


CONNECTION_ARGS = scalardb_config.get(
    'connection_args', {'host': 'localhost', 'port': 9200})


class ScalarStore(ElasticSearchBM25Retriever):
    def __init__(self, index_name: str, client: Any = elasticsearch.Elasticsearch(**CONNECTION_ARGS)):
        super().__init__(client=client, index_name=index_name)

    def insert(self, data: Iterable[str]):
        '''Insert data'''
        ids = self.add_texts(texts=data)
        return len(ids)

    def search(self, query: str):
        '''Query data'''
        res_docs = self.get_relevant_documents(query=query)
        return res_docs

    @classmethod
    def connect(cls, connection_args: dict = CONNECTION_ARGS):
        client = elasticsearch.Elasticsearch(**connection_args)
        return client

    @classmethod
    def drop(cls, project: str, connection_args: dict = CONNECTION_ARGS):
        client = cls.connect(connection_args)
        confirm = input(f'Confirm to drop table {project} scalar db (y/n): ')
        if confirm == 'y':
            try:
                client.indices.delete(index=project)
            except Exception as e:
                raise RuntimeError from e
        else:
            raise RuntimeError('Exiting ...')

    @classmethod
    def has_project(cls, project: str, connection_args: dict = CONNECTION_ARGS):
        client = cls.connect(connection_args)
        return client.indices.exists(index=project)
