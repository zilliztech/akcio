import logging
from typing import List

from langchain.agents import Tool, AgentExecutor

from data_loader import DataLoader
from store import VectorStore, MemoryStore
from embedding import TextEncoder
from llm import ChatAI
from agent import ChatAgent


logger = logging.getLogger(__name__)

encoder = TextEncoder()
chat_llm = ChatAI()
load_data = DataLoader()


def chat(session_id, project, question):
    '''Chat API'''
    vector_db = VectorStore(table_name=project, embedding_func=encoder)
    memory_db = MemoryStore(table_name=project, session_id=session_id)

    assert vector_db.col, f'Project {project} is not found in vector db.'

    tools = [
        Tool(
            name='Search',
            func=vector_db.search,
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
    vector_db = VectorStore(table_name=project, embedding_func=encoder)
    docs = load_data(data_src=data_src, source_type=source_type)
    num = vector_db.insert(docs)
    return num


def drop(project):
    '''Drop project will clean both vector and memory stores.'''
    # Clear vector db
    try:
        vector_db = VectorStore(table_name=project, embedding_func=encoder)
        vector_db.drop()
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
        doc_check = VectorStore.has_project(project)
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
    
def load(document_strs: List[str], project: str):
    '''Load doc embeddings to project table in vector store given a list of doc chunks.'''
    vector_db = VectorStore(table_name=project, embedding_func=encoder)
    num = vector_db.insert(document_strs)
    return num
    


if __name__ == '__main__':
    project = 'akcio'
    data_src = './requirements.txt'
    session_id = 'test000'
    question = 'What does it mean?'

    # count = insert(data_src=data_src, project=project)
    # print(check(project))

    answer = chat(project=project, session_id=session_id, question=question)
    print(answer)
    print(check(project))
    print(get_history(project, session_id))

    # drop(project=project)
    # print(check(project))