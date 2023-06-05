import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

from src.operations import chat, insert, drop


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
    except Exception:  # pylint: disable=W0718
        return jsonable_encoder({'status': False, 'msg': 'Failed to answer question.', 'code': 400}), 400


@app.post('/project/add')
def do_project_add_api(data_src: str, project: str, source_type: str = 'file'):
    try:
        num = insert(data_src=data_src, project=project, source_type=source_type)
        return jsonable_encoder({'status': True, 'msg': f'Successfully inserted doc chunks: {num}'}), 200
    except Exception as e:  # pylint: disable=W0718
        return jsonable_encoder({'status': False, 'msg': f'Failed to load data:\n{e}'}), 400


@app.post('/project/drop')
def do_project_drop_api(project: str):
    # Drop data in vector db
    try:
        drop(project=project)
        return jsonable_encoder({'status': True, 'msg': f'Dropped project: {project}'}), 200
    except Exception as e:  # pylint: disable=W0718
        return jsonable_encoder({'status': False, 'msg': f'Failed to drop project:\n{e}'}), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8900)
