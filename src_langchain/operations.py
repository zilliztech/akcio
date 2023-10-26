import os
import sys
import logging
from typing import List

from langchain.agents import Tool, AgentExecutor
from langchain.chains import ConversationalRetrievalChain

sys.path.append(os.path.dirname(__file__))

from agent import ChatAgent  # pylint: disable=C0413
from llm import ChatLLM  # pylint: disable=C0413
from embedding import TextEncoder  # pylint: disable=C0413
from store import MemoryStore, DocStore  # pylint: disable=C0413
from data_loader import DataParser  # pylint: disable=C0413

logger = logging.getLogger(__name__)

encoder = TextEncoder()
chat_llm = ChatLLM()
load_data = DataParser()


def chat(session_id, project, question, enable_agent=False):
    '''Chat API'''
    doc_db = DocStore(
        table_name=project,
        embedding_func=encoder,
    )
    memory_db = MemoryStore(table_name=project, session_id=session_id)

    if enable_agent:  # use agent
        memory_db.memory.output_key = None
        tools = [
            Tool(
                name='Search',
                func=doc_db.search,
                description='useful for search professional knowledge and information'
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
            return question, final_answer
        except Exception as e:  # pylint: disable=W0703
            return question, f'Something went wrong:\n{e}'
    else:  # use chain
        memory_db.memory.output_key = 'answer'
        qa = ConversationalRetrievalChain.from_llm(
            llm=chat_llm,
            retriever=doc_db.vector_db.as_retriever(),
            memory=memory_db.memory,
            return_generated_question=True
        )
        qa_result = qa(question)
        return qa_result['generated_question'], qa_result['answer']


def insert(data_src, project, source_type: str = 'file'):
    '''Load project docs will load docs from data source and then insert doc embeddings into the project table in the vector store.
    If there is no project table, it will create one.
    '''
    doc_db = DocStore(table_name=project,
                      embedding_func=encoder)
    docs, token_count = load_data(data_src=data_src, source_type=source_type)
    num = doc_db.insert(docs)
    return num, token_count


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
    '''Check existences of project tables in both doc stores and memory stores.'''
    try:
        doc_check = DocStore.has_project(project)
    except Exception as e:
        logger.error('Failed to check doc stores:\n%s', e)
        raise RuntimeError from e
    # Check memory
    try:
        memory_check = MemoryStore.check(project)
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e
    return {'store': doc_check, 'memory': memory_check}


def count(project):
    '''Count entities.'''
    try:
        counts = DocStore.count_entities(project=project)
        return counts
    except Exception as e:
        logger.error('Failed to count entities:\n%s', e)
        raise RuntimeError from e


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
        raise RuntimeError(f'Failed to clear memory:\n{e}') from e


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
