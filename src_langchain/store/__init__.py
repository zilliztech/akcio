import os
import sys
from typing import Optional, List

from .vector_store.milvus import VectorStore, Embeddings
from .memory_store.pg import MemoryStore

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import USE_SCALAR  # pylint: disable=C0413

if USE_SCALAR:
    from .scalar_store.es import ScalarStore


class DocStore:
    '''Integrate vector store and scalar store.'''

    def __init__(
            self,
            table_name: str,
            embedding_func: Embeddings = None,
            use_scalar: bool = USE_SCALAR
    ) -> None:
        self.table_name = table_name
        self.use_scalar = use_scalar
        self.embedding_func = embedding_func

        self.vector_db = VectorStore(
            table_name=table_name, embedding_func=self.embedding_func)

        if self.use_scalar:
            self.scalar_db = ScalarStore(index_name=table_name)
        else:
            self.scalar_db = None

    def search(self, query: str):
        res = []
        pages = []
        for doc in self.vector_db.search(query):
            if doc.page_content not in pages:
                res.append(doc)
                pages.append(doc.page_content)
        if self.scalar_db:
            for doc in self.scalar_db.search(query):
                if doc.page_content not in pages:
                    res.append(doc)
                    pages.append(doc.page_content)
        return res

    def insert(self, data: List[str], metadatas: Optional[List[dict]] = None):
        vec_count = None
        scalar_count = None
        vec_count = self.vector_db.insert(data=data, metadatas=metadatas)
        if metadatas and 'doc' in metadatas[0]:
            data = [doc['doc'] for doc in metadatas]
        if self.scalar_db:
            scalar_count = self.scalar_db.insert(data=data)
        if vec_count and scalar_count:
            assert vec_count == scalar_count, f'Data count does not match: {vec_count} in vector db VS {scalar_count} in scalar db.'
        return vec_count

    def insert_embeddings(self, data: List[float], metadatas: List[dict]):
        vec_count = None
        scalar_count = None
        docs = []
        for d in metadatas:
            assert 'text' in d, 'Embedding insert must have corresponding text in metadatas.'
            if 'doc' in d:
                docs.append(d['doc'])
            else:
                docs.append(d['text'])
        vec_count = self.vector_db.insert_embeddings(
            data=data, metadatas=metadatas)
        if self.scalar_db:
            scalar_count = self.scalar_db.insert(data=docs)
        if vec_count and scalar_count:
            assert vec_count == scalar_count, f'Data count does not match: {vec_count} in vector db VS {scalar_count} in scalar db.'
        return vec_count

    @classmethod
    def drop(cls, project):
        status = cls.has_project(project)
        assert status, f'No table found for project: {project}'

        VectorStore.drop(project)

        if USE_SCALAR:
            ScalarStore.drop(project)

        status = cls.has_project(project)
        assert not status, f'Failed to drop table for project: {project}'


    @classmethod
    def has_project(cls, project):
        status = VectorStore.has_project(project)
        if USE_SCALAR:
            assert ScalarStore.has_project(project) == status
        return status
