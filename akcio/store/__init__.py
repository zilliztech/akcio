from typing import Optional, List

from .vector_store.milvus import VectorStore, Embeddings
from .scalar_store.es import ScalarStore
from .memory_store.pg import MemoryStore


class DocStore:
    '''Integrate vector store and scalar store.'''

    def __init__(
            self,
            table_name: str,
            embedding_func: Embeddings = None,
            use_scalar: bool = True
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
    def drop(cls, project: str):
        status = cls.has_project(project)
        assert status['vector store'], f'No table in vector db: {project}'
        assert status['scalar store'], f'No table in scalar db: {project}'

        VectorStore.drop(project)
        ScalarStore.drop(project)

        status = cls.has_project(project)
        assert not status['vector store'], f'Failed to drop table in vector db: {project}'
        assert not status['scalar store'], f'Failed to drop table in scalar db: {project}'

    @classmethod
    def has_project(cls, project):
        status = {}
        status['vector store'] = VectorStore.has_project(project)
        status['scalar store'] = ScalarStore.has_project(project)
        return status
