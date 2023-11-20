import os
import unittest

from src.towhee.base import BaseMemory
from src.towhee.memory.sql import MemoryStore


class TestSql(unittest.TestCase):
    '''SQL test'''
    project = 'akcio_ut'
    session_id = 'test000'
    messages = [('test question', 'test answer')]

    db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')
    test_config = {'connect_str': f'sqlite:///{db_path}'}
    memory = MemoryStore(configs=test_config)

    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

        assert isinstance(cls.memory, BaseMemory)
        assert hasattr(cls.memory, 'add_history')
        assert hasattr(cls.memory, 'get_history')
        assert hasattr(cls.memory, 'drop')
        assert hasattr(cls.memory, 'check')

    def test_history(self):
        self.memory.add_history(self.project, self.session_id, self.messages)
        history = self.memory.get_history(self.project, self.session_id)
        assert history == self.messages

    def test_utils(self):
        self.memory.add_history(self.project, self.session_id, self.messages)
        assert self.memory.check(self.project)

        self.memory.drop(self.project, self.session_id)
        history = self.memory.get_history(self.project, self.session_id)
        assert history == []

        self.memory.drop(self.project)
        assert not self.memory.check(self.project)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.db_path)


if __name__ == '__main__':
    unittest.main()
