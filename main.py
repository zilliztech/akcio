import argparse

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder


# Specify mode
parser = argparse.ArgumentParser(description='Start service with different modes.')
parser.add_argument('--langchain', action='store_true')
parser.add_argument('--towhee', action='store_true')

args = parser.parse_args()

USE_LANGCHAIN = args.langchain
USE_TOWHEE = args.towhee

assert (USE_LANGCHAIN and not USE_TOWHEE ) or (USE_TOWHEE and not USE_LANGCHAIN), \
    'The service should start with either "--langchain" or "--towhee".'

if USE_LANGCHAIN:
    from src_langchain.operations import chat, insert, drop  # pylint: disable=C0413
if USE_TOWHEE:
    from src_towhee.operations import chat, insert, drop  # pylint: disable=C0413

app = FastAPI()
origins = ['*']

@app.get('/')
def check_api():
    return jsonable_encoder({'status': True, 'msg': 'ok'}), 200

@app.get('/answer')
def do_answer_api(session_id: str, project: str, question: str):
    try:
        final_answer = chat(session_id=session_id,
                            project=project, question=question)
        assert isinstance(final_answer, str)
        return jsonable_encoder({'status': True, 'msg': final_answer}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to answer question:\n{e}', 'code': 400}), 400


@app.post('/project/add')
def do_project_add_api(data_src: str, project: str, source_type: str = 'file'):
    try:
        num = insert(data_src=data_src, project=project, source_type=source_type)
        return jsonable_encoder({'status': True, 'msg': f'Successfully inserted doc chunks: {num}'}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to load data:\n{e}'}), 400


@app.post('/project/drop')
def do_project_drop_api(project: str):
    # Drop data in vector db
    try:
        drop(project=project)
        return jsonable_encoder({'status': True, 'msg': f'Dropped project: {project}'}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to drop project:\n{e}'}), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8900)
