import os
import argparse
import uuid

import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import PlainTextResponse

from config import TEMP_DIR

os.makedirs(TEMP_DIR, exist_ok=True)
os.environ['PROMETHEUS_DISABLE_CREATED_SERIES'] = 'true'

# Specify mode
parser = argparse.ArgumentParser(description='Start service with different modes.')
parser.add_argument('--langchain', action='store_true')
parser.add_argument('--towhee', action='store_true')
parser.add_argument('--moniter', action='store_true')
parser.add_argument('--max_observation', default=1000)
parser.add_argument('--name', default=str(uuid.uuid4()))
args = parser.parse_args()

app = FastAPI()
origins = ['*']

# Apply args
USE_LANGCHAIN = args.langchain
USE_TOWHEE = args.towhee
MAX_OBSERVATION = args.max_observation
ENABLE_MONITER = args.moniter
NAME = args.name

assert (USE_LANGCHAIN and not USE_TOWHEE ) or (USE_TOWHEE and not USE_LANGCHAIN), \
    'The service should start with either "--langchain" or "--towhee".'

if USE_LANGCHAIN:
    from src_langchain.operations import chat, insert, drop, check, get_history, clear_history, count  # pylint: disable=C0413
if USE_TOWHEE:
    from src_towhee.operations import chat, insert, drop, check, get_history, clear_history, count  # pylint: disable=C0413
if ENABLE_MONITER:
    from moniter import enable_moniter  # pylint: disable=C0413
    from prometheus_client import generate_latest, REGISTRY  # pylint: disable=C0413

    enable_moniter(app, MAX_OBSERVATION, NAME)

    @app.get('/metrics')
    async def metrics():
        registry = REGISTRY
        data = generate_latest(registry)
        return PlainTextResponse(content=data, media_type='text/plain')


@app.get('/')
def check_api():
    res = jsonable_encoder({'status': True, 'msg': 'ok'}), 200
    return res


@app.get('/answer')
def do_answer_api(session_id: str, project: str, question: str):
    try:
        new_question, final_answer = chat(session_id=session_id, project=project, question=question)
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
            chunk_num, token_count = insert(data_src=url, project=project, source_type='url')
        if file:
            temp_file = os.path.join(TEMP_DIR, file.filename)
            with open(temp_file, 'wb') as f:
                content = file.file.read()
                f.write(content)
            chunk_num, token_count = insert(data_src=temp_file, project=project, source_type='file')
        return jsonable_encoder({'status': True, 'msg': {
            'chunk count': chunk_num,
            'token count': token_count
        }}), 200
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
