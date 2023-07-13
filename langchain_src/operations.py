import os
import sys
import logging
from typing import List

from langchain.agents import Tool, AgentExecutor

sys.path.append(os.path.dirname(__file__))

from data_loader import DataParser  # pylint: disable=C0413
from store import MemoryStore, DocStore  # pylint: disable=C0413
from embedding import TextEncoder  # pylint: disable=C0413
from llm import ChatLLM  # pylint: disable=C0413
from agent import ChatAgent  # pylint: disable=C0413


logger = logging.getLogger(__name__)

encoder = TextEncoder()
chat_llm = ChatLLM()
load_data = DataParser()


def chat(session_id, project, question):
    '''Chat API'''
    doc_db = DocStore(
        table_name=project,
        embedding_func=encoder,
        )
    memory_db = MemoryStore(table_name=project, session_id=session_id)

    tools = [
        Tool(
            name='Search',
            func=doc_db.search,
            description='Search through Milvus.'
        )
    ]
    agent = ChatAgent.from_llm_and_tools(llm=chat_llm, tools=tools)
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory_db.memory,
        verbose=False
    )
    try:
        final_answer = agent_chain.run(input=question)
        return final_answer
    except Exception:
        return 'Something went wrong. Please clear history and try again!'


def insert(data_src, project, source_type: str = 'file'):
    '''Load project docs will load docs from data source and then insert doc embeddings into the project table in the vector store.
    If there is no project table, it will create one.
    '''
    doc_db = DocStore(table_name=project,
                      embedding_func=encoder)
    docs = load_data(data_src=data_src, source_type=source_type)
    num = doc_db.insert(docs)
    return num


def drop(project):
    '''Drop project will clean both vector and memory stores.'''
    # Clear vector db
    try:
        DocStore.drop(project)
    except Exception as e:
        logger.error('Failed to drop project:\n%s', e)
        raise RuntimeError from e
    # Clear memory
    try:
        memory_db = MemoryStore(table_name=project, session_id='')
        memory_db.drop(project)
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e


def check(project):
    '''Check existences of project tables in both vector and memory stores.'''
    try:
        doc_check = DocStore.has_project(project)
    except Exception as e:
        logger.error('Failed to check table in vector db:\n%s', e)
        raise RuntimeError from e
    # Clear memory
    try:
        memory_check = MemoryStore.check(project)
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e
    return {'store': doc_check, 'memory': memory_check}


def get_history(project, session_id):
    '''Get conversation history from memory store.'''
    try:
        memory_db = MemoryStore(table_name=project, session_id=session_id)
        messages = memory_db.get_history()
        return messages
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e
    

def clear_history(project, session_id):
    '''Clear conversation history from memory store.'''
    try:
        memory_db = MemoryStore(project, session_id)
        memory_db.drop(table_name=project, session_id=session_id)
    except Exception as e:
        raise RuntimeError(f'Failed to clear memory:\n{e}')


def load(document_strs: List[str], project: str):
    '''Load doc embeddings to project table in vector store given a list of doc chunks.'''
    doc_db = DocStore(table_name=project,
                      embedding_func=encoder)
    num = doc_db.insert(document_strs)
    return num


# if __name__ == '__main__':
#     project = 'akcio'
#     data_src = 'https://docs.towhee.io/'
#     session_id = 'test000'
#     question0 = 'What is your code name?'
#     question1 = 'What is Towhee?'
#     question2 = 'What does it do?'

#     count = insert(data_src=data_src, project=project, source_type='url')
#     print('\nCount:', count)
#     print('\nCheck:', check(project))
    
#     answer = chat(project=project, session_id=session_id, question=question0)
#     print('\nAnswer:', answer)

#     answer = chat(project=project, session_id=session_id, question=question1)
#     print('\nAnswer:', answer)

#     answer = chat(project=project, session_id=session_id, question=question2)
#     print('\nAnswer:', answer)

#     print('\nHistory:', get_history(project, session_id))
#     clear_history(project, session_id)
#     print('\nHistory:', get_history(project, session_id))

#     print('\nDropping project ...')
#     drop(project=project)
#     print(check(project))
