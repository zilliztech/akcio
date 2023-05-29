from typing import List
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import PostgresChatMessageHistory, ConversationBufferMemory

from ..config import memorydb_config


CONNECT_STR = memorydb_config.get('connect_str', 'postgresql://postgres:postgres@localhost/chat_history')


class MemoryStore:
    '''Memory database APIs: add_history, get_history'''

    def __init__(self, table_name: str, session_id: str):
        '''Initialize memory storage: e.g. history_db'''
        self.table_name = table_name
        self.session_id = session_id
        
        self.history_db = PostgresChatMessageHistory(
            table_name=self.table_name,
            session_id=self.session_id,
            connection_string=CONNECT_STR,
            )
        self.memory = ConversationBufferMemory(
            memory_key='chat_history',
            chat_memory=self.history_db,
            return_messages=True
        )

    def add_history(self, messages: List[dict]):
        for qa in messages:
            if 'question' in qa:
                self.history_db.add_user_message(qa['question'])
            if 'answer' in qa:
                self.history_db.add_ai_message(qa['answer'])

    def get_history(self):
        history = self.history_db.messages
        messages = []
        for x in history:
            if isinstance(x, HumanMessage):
                if len(messages) > 0 and messages[-1][0] is None:
                    a = messages[-1][-1]
                    del messages[-1]
                else:
                    a = None
                messages.append((x.content, a))
            if isinstance(x, AIMessage):
                if len(messages) > 0 and messages[-1][-1] is None:
                    q = messages[-1][0]
                    del messages[-1]
                else:
                    q = None
                messages.append((q, x.content))
        return messages
    

    @classmethod
    def connect(cls, connect_str: str = CONNECT_STR):
        import psycopg
        from psycopg.rows import dict_row

        connection = psycopg.connect(connect_str)
        cursor = connection.cursor(row_factory=dict_row)
        return connection, cursor
    
    @classmethod
    def drop(cls, table_name, connect_str: str = CONNECT_STR):
        connection, cursor = cls.connect(connect_str)

        existence = cls.check(table_name)
        query = f'DROP TABLE {table_name};'
        cursor.execute(query)
        connection.commit()
        
        existence = cls.check(table_name=table_name)
        assert not existence, f'Failed to drop table {table_name}.'

    @classmethod 
    def check(cls, table_name, connect_str: str = CONNECT_STR):
        _, cursor = cls.connect(connect_str)
        
        check = f'SELECT COUNT(*) FROM pg_class WHERE relname = %s;'
        cursor.execute(check, (table_name,))
        record = cursor.fetchall()
        if record[0]['count'] > 0:
            return True
        else:
            return False