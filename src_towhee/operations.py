import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src_towhee.pipelines import TowheePipelines  # pylint: disable=C0413
from src_towhee.memory import MemoryStore  # pylint: disable=C0413


logger = logging.getLogger(__name__)


towhee_pipelines = TowheePipelines()
memory_store = MemoryStore()

# Initiate pipelines
insert_pipeline = towhee_pipelines.insert_pipeline
search_pipeline = towhee_pipelines.search_pipeline


def chat(session_id, project, question):
    '''Chat API'''
    try:
        history = memory_store.get_history(project, session_id)
        res = search_pipeline(question, history, project).get()
        if len(res) == 2:
            new_question, final_answer = res
        elif len(res) == 1:
            new_question = question
            final_answer = res[0]
        else:
            raise RuntimeError(f'Invalid pipeline outputs: {res}')
        # Update history
        messages = [(question, final_answer)]
        memory_store.add_history(project, session_id, messages)
        return new_question, final_answer
    except Exception as e: # pylint: disable=W0703
        return question, f'Something went wrong:\n{e}'


def insert(data_src, project, source_type: str = 'file'): # pylint: disable=W0613
    '''Load project docs will load docs from data source and then insert doc embeddings into the project table in the vector store.
    If there is no project table, it will create one.
    '''
    if not towhee_pipelines.check(project):
        towhee_pipelines.create(project)
    res = insert_pipeline(data_src, project).to_list()
    num = towhee_pipelines.count_entities(project)['vector store']
    assert len(res) <= num, 'Failed to insert data.'
    return len(res)


def drop(project):
    '''Drop project will clean both vector and memory stores.'''
    status = check(project)
    # Clear vector db
    try:
        if status['store']:
            towhee_pipelines.drop(project)
        else:
            logger.warning('No store for the project.')
    except Exception as e:
        logger.error('Failed to drop project:\n%s', e)
        raise RuntimeError from e
    # Clear memory
    try:
        if status['memory']:
            memory_store.drop(project)
        else:
            logger.warning('No memory for the project.')
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e


def check(project):
    '''Check existences of project tables in both vector and memory stores.'''
    try:
        doc_check = towhee_pipelines.check(project)
    except Exception as e:
        logger.error('Failed to check doc stores:\n%s', e)
        raise RuntimeError from e
    # Check memory
    try:
        memory_check = memory_store.check(project)
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e
    return {'store': doc_check, 'memory': memory_check}


def count(project):
    '''Count entities.'''
    try:
        counts = towhee_pipelines.count_entities(project)
        return counts
    except Exception as e:
        logger.error('Failed to count entities:\n%s', e)
        raise RuntimeError from e


def get_history(project, session_id):
    '''Get conversation history from memory store.'''
    try:
        messages = memory_store.get_history(project, session_id)
        return messages
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e


def clear_history(project, session_id):
    '''Clear conversation history from memory store.'''
    try:
        memory_store.drop(project, session_id)
    except Exception as e:
        raise RuntimeError(f'Failed to clear memory:\n{e}') from e


# if __name__ == '__main__':
#     project = 'akcio_test'
#     data_src = 'https://towhee.io'
#     session_id = 'test000'
#     question0 = 'What is your code name?'
#     question1 = 'What is Towhee?'
#     question2 = 'What does it do?'

#     count = insert(data_src=data_src, project=project, source_type='url')
#     print('\nCount:', count)
#     print('\nCheck:', check(project))

#     new_question, answer = chat(project=project, session_id=session_id, question=question0)
#     print('\n' + new_question, '\n' + answer)

#     new_question, answer = chat(project=project, session_id=session_id, question=question1)
#     print('\n' + new_question, '\n' + answer)

#     new_question, answer = chat(project=project, session_id=session_id, question=question2)
#     print('\n' + new_question, '\n' + answer)
#     print('\nHistory:', get_history(project, session_id))

#     clear_history(project, session_id)
#     print('\nHistory:', get_history(project, session_id))

#     print('\nDropping project ...')
#     drop(project=project)
#     print(check(project))
