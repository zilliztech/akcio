import unittest
from unittest.mock import patch

from towhee.runtime.data_queue import DataQueue, ColumnType

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


class MockStore:
    def __init__(self, *args, **kwargs):
        self.memory = []

    def get_history(self, *args, **kwargs):
        return self.memory

    def add_history(self, project, session_id, messages: list):
        self.memory += messages

    def drop(self, *args, **kwargs):
        self.memory = []

    def check(self, *args, **kwargs):
        return len(self.memory) > 0


class MockPipeline:
    def __init__(self, *args, **kwargs):
        self.search_que = DataQueue([('answer', ColumnType.SCALAR)])
        self.insert_que = DataQueue([('data', ColumnType.SCALAR)])
        self.projects = {}

    def search_pipeline(self, *args, **kwargs):
        self.search_que.put([('mock answer')])
        self.search_que.seal()
        return self.search_que

    def insert_pipeline(self, data_src, project, source_type='file'):
        self.projects[project] = [data_src]
        self.insert_que.put([{'milvus': len(data_src), 'es': None, 'token_count': len(data_src.split(' '))}])
        self.insert_que.seal()
        return self.insert_que

    def check(self, project):
        return project in self.projects

    def create(self, project):
        if not self.check(project):
            self.projects[project] = ''

    def count_entities(self, project):
        return {'vector store': len(self.projects[project]), 'scalar store': None}

    def drop(self, project):
        del self.projects[project]


class TestOperations(unittest.TestCase):
    '''Test operations'''
    session_id = 'test000'
    project = 'akcio_ut'
    test_src = 'test src'
    expect_len = 1
    expect_token_count = len(test_src.split(' '))
    question = 'the first question'
    expect_answer = 'mock answer'

    def test_chat(self):

        with patch('src_towhee.pipelines.TowheePipelines') as mock_pipelines, \
                patch('src_towhee.memory.MemoryStore') as mock_memory:
            mock_pipelines.return_value = MockPipeline()
            mock_memory.return_value = MockStore()

            from src_towhee.pipelines import TowheePipelines
            from src_towhee.memory import MemoryStore

            with patch.object(TowheePipelines, 'search_pipeline', mock_pipelines.search_pipeline), \
                    patch.object(MemoryStore, 'add_history', mock_memory.add_history), \
                    patch.object(MemoryStore, 'get_history', mock_memory.get_history), \
                    patch.object(MemoryStore, 'drop', mock_memory.drop):

                from src_towhee.operations import chat, get_history, clear_history

                question, answer = chat(
                    self.session_id, self.project, self.question)
                assert answer == self.expect_answer

                history = get_history(self.project, self.session_id)
                assert history == [(self.question, self.expect_answer)]

                clear_history(self.project, self.session_id)
                clean_history = get_history(self.project, self.session_id)
                assert clean_history == []

    def test_insert(self):

        with patch('src_towhee.pipelines.TowheePipelines') as mock_pipelines, \
                patch('src_towhee.memory.MemoryStore') as mock_memory:
            mock_pipelines.return_value = MockPipeline()
            mock_memory.return_value = MockStore()

            from src_towhee.pipelines import TowheePipelines
            from src_towhee.memory import MemoryStore

            with patch.object(TowheePipelines, 'insert_pipeline', mock_pipelines.insert_pipeline), \
                    patch.object(TowheePipelines, 'count_entities', mock_pipelines.count_entities), \
                    patch.object(TowheePipelines, 'check', mock_pipelines.check), \
                    patch.object(TowheePipelines, 'drop', mock_pipelines.drop), \
                    patch.object(MemoryStore, 'check', mock_memory.check), \
                    patch.object(MemoryStore, 'drop', mock_memory.drop):

                from src_towhee.operations import insert, check, drop

                chunk_count, token_count = insert(self.test_src, self.project)
                assert chunk_count == self.expect_len, token_count == self.expect_token_count
                status = check(self.project)
                assert status['store']

                drop(self.project)
                status = check(self.project)
                assert not status['store']
                assert not status['memory']


if __name__ == '__main__':
    unittest.main()
