import sys
import os
import json
from typing import List, Dict

from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, Integer, JSON


sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import MEMORYDB_CONFIG
from src_towhee.base import BaseMemory

        
class MemoryStore(BaseMemory):
    '''Memory store using SQL databases supported by sqlalchemy. (eg. Postgresql)'''
    def __init__(self, configs: Dict = MEMORYDB_CONFIG):
        '''Initialize memory storage'''
        self.engine = create_engine(url=configs['connect_str'])
        self.meta = MetaData()

    def add_history(self, project: str, session_id: str, messages: List[dict]):
        project_table = self._create_table_if_not_exists(project)

        data = [
            {'session_id': session_id, 'message': json.dumps(self._message_to_dict(message))}
            for message in messages
            ]
        with self.engine.connect() as conn:
            query = project_table.insert()
            conn.execute(query, data)
            conn.commit()

    def get_history(self, project: str, session_id: str):
        if self.check(project):
            project_table = Table(project, self.meta, autoload_with=self.engine)
            query = project_table.select().where(project_table.c.session_id == session_id)
            messages = []
            with self.engine.connect() as conn:
                for row in conn.execute(query):
                    message = row.message
                    if isinstance(message, str):
                        message = json.loads(message)
                    message = self._message_from_dict(message)
                    messages.append(message)
        else:
            messages = []
        return messages

    def _create_table_if_not_exists(self, project):
        if not self.check(project):
            project_table = Table(project, self.meta,
                                Column('id', Integer, primary_key=True, autoincrement=True),
                                Column('session_id', String, nullable=False),
                                Column('message', JSON, nullable=False)
                                )
            self.meta.create_all(self.engine)
        project_table = Table(project, self.meta, autoload_with=self.engine)
        return project_table
        
    def drop(self, project, session_id=None):
        if self.check(project):
            project_table = Table(project, self.meta, autoload_with=self.engine)
            if session_id and len(session_id) > 0:
                query = project_table.delete().where(project_table.c.session_id == session_id)
                with self.engine.connect() as conn:
                    conn.execute(query)
                    conn.commit()
            else:
                query = project_table.drop(self.engine)

        if not session_id or len(session_id) == 0:
            existence = self.check(project)
            assert not existence, f'Failed to drop table {project}.'

    def check(self, project):
        return inspect(self.engine).has_table(project)
    
    @staticmethod
    def _message_from_dict(message: dict):
        return tuple(message['data'])
    
    @staticmethod
    def _message_to_dict(message: tuple) -> dict:
        return {'type': 'chat', 'data': message}


# if __name__ == '__main__':
#     project = 'akcio_memory'
#     session_id = 'test000'
#     memory = MemoryStore()
#     messages = [('hello, q', 'hi, a')]

#     print(memory.check(project))
#     print(memory.get_history(project, session_id))

#     memory.add_history(project, session_id, messages)
#     print(memory.get_history(project, session_id))

#     memory.drop(project, session_id)
#     print(memory.get_history(project, session_id))

#     memory.drop(project)
#     print(memory.check(project))