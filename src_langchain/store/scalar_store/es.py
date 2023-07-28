import os
import sys
from typing import Any, Iterable

import elasticsearch
from langchain.retrievers import ElasticSearchBM25Retriever

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import SCALARDB_CONFIG  # pylint: disable=C0413


CONNECTION_ARGS = SCALARDB_CONFIG.get(
    'connection_args', {'host': 'localhost', 'port': 9200})


class ScalarStore(ElasticSearchBM25Retriever):
    '''Scalar store to save and retrieve scalar data.'''
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

    @staticmethod
    def connect(connection_args: dict = CONNECTION_ARGS):
        client = elasticsearch.Elasticsearch(**connection_args)
        return client

    @staticmethod
    def drop(project: str, connection_args: dict = CONNECTION_ARGS):
        client = ScalarStore.connect(connection_args)
        # confirm = input(f'Confirm to drop table {project} scalar db (y/n): ')
        # if confirm == 'y':
        try:
            client.indices.delete(index=project)
        except Exception as e:
            raise RuntimeError from e

    @staticmethod
    def has_project(project: str, connection_args: dict = CONNECTION_ARGS):
        client = ScalarStore.connect(connection_args)
        return client.indices.exists(index=project)
