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

    final_answer = agent_chain.run(input=question)

    # try:
    #     new_history = [
    #         {'question': question, 'answer': final_answer}
    #     ]
    #     memory_db.add_history(messages=new_history)
    # except Exception as e:
    #     logger.error(f'Failed to add history:\n{e}')
    return final_answer


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
    return {'vector db': doc_check, 'memory': memory_check}


def get_history(project, session_id):
    '''Get conversation history from memory store.'''
    try:
        memory_db = MemoryStore(table_name=project, session_id=session_id)
        messages = memory_db.get_history()
        return messages
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e


def load(document_strs: List[str], project: str):
    '''Load doc embeddings to project table in vector store given a list of doc chunks.'''
    doc_db = DocStore(table_name=project,
                      embedding_func=encoder)
    num = doc_db.insert(document_strs)
    return num


# if __name__ == '__main__':
#     project = 'akcio'
#     data_src = '../requirements.txt'
#     session_id = 'test000'
#     question = 'What version is required for LangChain?'

#     count = insert(data_src=data_src, project=project)
#     print('Count:', count)
#     print('Check:', check(project))

#     answer = chat(project=project, session_id=session_id, question=question)
#     print('Answer:', answer)
#     print('Check:', check(project))
#     print('History:', get_history(project, session_id))

#     drop(project=project)
#     print(check(project))
