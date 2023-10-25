import os
import sys
from typing import List

from sqlalchemy import create_engine, inspect, MetaData, Table

from langchain.schema import HumanMessage, AIMessage
from langchain.memory import SQLChatMessageHistory, ConversationBufferMemory

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import MEMORYDB_CONFIG  # pylint: disable=C0413


CONNECT_STR = MEMORYDB_CONFIG.get(
    'connect_str', 'sqlite:///./sqlite.db')


class MemoryStore:
    '''Memory database APIs: add_history, get_history'''

    def __init__(self, table_name: str, session_id: str):
        '''Initialize memory storage: e.g. history_db'''
        self.table_name = table_name
        self.session_id = session_id

        self.history_db = SQLChatMessageHistory(
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

    @staticmethod
    def drop(table_name, connect_str: str = CONNECT_STR, session_id: str = None):
        engine = create_engine(connect_str, echo=False)
        existence = MemoryStore.check(table_name)

        if existence:
            project_table = Table(table_name, MetaData(),
                                  autoload_with=engine, extend_existing=True)
            if session_id and len(session_id) > 0:
                query = project_table.delete().where(project_table.c.session_id == session_id)
                with engine.connect() as conn:
                    conn.execute(query)
                    conn.commit()
            else:
                query = project_table.drop(engine)

    @staticmethod
    def check(table_name, connect_str: str = CONNECT_STR):
        engine = create_engine(connect_str, echo=False)
        return inspect(engine).has_table(table_name)
