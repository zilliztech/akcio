import logging
from typing import List

from langchain.agents import Tool, AgentExecutor

from data_loader import DataLoader
from store import MemoryStore, DocStore
from embedding import TextEncoder
from llm import ChatAI
from agent import ChatAgent


logger = logging.getLogger(__name__)

encoder = TextEncoder()
chat_llm = ChatAI()
load_data = DataLoader()


def chat(session_id, project, question, enable_es: bool = False):
    '''Chat API'''
    doc_db = DocStore(table_name=project, embedding_func=encoder, use_scalar=enable_es)
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


def insert(data_src, project, source_type: str = 'file', enable_es: bool = True):
    '''Load project docs will load docs from data source and then insert doc embeddings into the project table in the vector store.
    If there is no project table, it will create one.
    '''
    doc_db = DocStore(table_name=project, embedding_func=encoder, use_scalar=enable_es)
    docs = load_data(data_src=data_src, source_type=source_type)
    num = doc_db.insert(docs)
    return num


def drop(project):
    '''Drop project will clean both vector and memory stores.'''
    # Clear vector db
    try:
        doc_db = DocStore(table_name=project, embedding_func=encoder, use_scalar=True)
        doc_db.drop()
    except Exception as e:
        logger.error(f'Failed to drop table in vector db:\n{e}')
        raise RuntimeError(e)
    # Clear memory
    try:
        memory_db = MemoryStore(table_name=project, session_id='')
        memory_db.drop(project)
    except Exception as e:
        logger.error(f'Failed to clean memory for the project:\n{e}')
        raise RuntimeError(e)

 
def check(project):
    '''Check existences of project tables in both vector and memory stores.'''
    try:
        doc_check = DocStore.has_project(project)
    except Exception as e:
        logger.error(f'Failed to check table in vector db:\n{e}')
        raise RuntimeError(e)
    # Clear memory
    try:
        memory_check = MemoryStore.check(project)
    except Exception as e:
        logger.error(f'Failed to clean memory for the project:\n{e}')
        raise RuntimeError(e)
    return {'vector db': doc_check, 'memory': memory_check}

def get_history(project, session_id):
    '''Get conversation history from memory store.'''
    try:
        memory_db = MemoryStore(table_name=project, session_id=session_id)
        messages = memory_db.get_history()
        return messages
    except Exception as e:
        logger.error(f'Failed to clean memory for the project:\n{e}')
        raise RuntimeError(e)


def load(document_strs: List[str], project: str, enable_es: bool = True):
    '''Load doc embeddings to project table in vector store given a list of doc chunks.'''
    doc_db = DocStore(table_name=project, embedding_func=encoder, use_scalar=enable_es)
    num = doc_db.insert(document_strs)
    return num
    


if __name__ == '__main__':
    project = 'akcio'
    data_src = './requirements.txt'
    session_id = 'test000'
    question = 'What does it mean?'

    # count = insert(data_src=data_src, project=project, enable_es=False)
    # print(check(project))

    # answer = chat(project=project, session_id=session_id, question=question, enable_es=False)
    # print(answer)
    # print(check(project))
    # print(get_history(project, session_id))

    drop(project=project)
    print(check(project))