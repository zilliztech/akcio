import argparse
import os

import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.encoders import jsonable_encoder

from config import TEMP_DIR


os.makedirs(TEMP_DIR, exist_ok=True)

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
    from src_langchain.operations import chat, insert, drop, check, get_history, clear_history, count  # pylint: disable=C0413
if USE_TOWHEE:
    from src_towhee.operations import chat, insert, drop, check, get_history, clear_history, count  # pylint: disable=C0413

app = FastAPI()
origins = ['*']

@app.get('/')
def check_api():
    return jsonable_encoder({'status': True, 'msg': 'ok'}), 200

@app.get('/answer')
def do_answer_api(session_id: str, project: str, question: str):
    try:
        new_question, final_answer = chat(session_id=session_id,
                            project=project, question=question)
        assert isinstance(final_answer, str)
        return jsonable_encoder({
            'status': True,
            'msg': final_answer,
            'debug': {
                'original question': question,
                'modified question': new_question,
                'answer': final_answer,
            }
            }), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to answer question:\n{e}', 'code': 400}), 400


@app.post('/project/add')
def do_project_add_api(project: str, url: str = None, file: UploadFile = None):
    assert url or file, 'You need to upload file or enter url of document to add data.'
    try:
        if url:
            num = insert(data_src=url, project=project, source_type='url')
        if file:
            temp_file = os.path.join(TEMP_DIR, file.filename)
            with open(temp_file, 'wb') as f:
                content = file.file.read()
                f.write(content)
            num = insert(data_src=temp_file, project=project, source_type='file')
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


@app.get('/project/check')
def do_project_check_api(project: str):
    try:
        status = check(project)
        return jsonable_encoder({'status': True, 'msg': status}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to check project:\n{e}'}), 400


@app.get('/project/count')
def do_project_count_api(project: str):
    try:
        counts = count(project)
        return jsonable_encoder({'status': True, 'msg': counts}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to count entities:\n{e}'}), 400


@app.get('/history/get')
def do_history_get_api(project: str, session_id: str = None):
    try:
        history = get_history(project=project, session_id=session_id)
        return jsonable_encoder({'status': True, 'msg': history}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to get history:\n{e}'}), 400


@app.get('/history/clear')
def do_history_clear_api(project: str, session_id: str = None):
    try:
        clear_history(project=project, session_id=session_id)
        return jsonable_encoder({'status': True, 'msg': f'Successfully clear history for project {project} ({session_id}).'}), 200
    except Exception as e:  # pylint: disable=W0703
        return jsonable_encoder({'status': False, 'msg': f'Failed to clear history:\n{e}'}), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8900)
