from config import CHAT_CONFIG, TEXTENCODER_CONFIG, VECTORDB_CONFIG, RERANK_CONFIG  # pylint: disable=C0413
from src_towhee.pipelines import TowheePipelines  # pylint: disable=C0413
from src_towhee.base import BasePipelines  # pylint: disable=C0413
import unittest
from unittest.mock import patch

import json
import sys
import os

from milvus import default_server

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))


TEXTENCODER_CONFIG = {
    'model': 'paraphrase-albert-small-v2',
    'dim': 768,
    'norm': False
}

VECTORDB_CONFIG['connection_args'] = {
    'uri': f'https://127.0.0.1:{default_server.listen_port}',
    # 'uri': 'https://localhost:19530',
    'user': None,
    'password': None,
    'secure': False
}

MOCK_ANSWER = 'mock answer'


def mock_prompt(question, context, history):
    return [{'question': question}]


def create_pipelines(llm_src):
    # Check llm_src has corresponding chat config
    assert llm_src in CHAT_CONFIG

    # Mock operator output
    pipelines = TowheePipelines(
        llm_src=llm_src,
        use_scalar=False,
        prompt_op=mock_prompt,
        textencoder_config=TEXTENCODER_CONFIG,
        vectordb_config=VECTORDB_CONFIG,
        rerank_config=RERANK_CONFIG
    )
    return pipelines


class TestPipelines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        default_server.cleanup()
        default_server.start()

    def test_openai(self):
        with patch('openai.ChatCompletion.create') as mock_llm:

            mock_llm.return_value = {'choices': [
                {'message': {'content': MOCK_ANSWER}}]}

            pipelines = create_pipelines('openai')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    def test_chatglm(self):
        with patch('zhipuai.model_api.invoke') as mock_llm:

            mock_llm.return_value = {
                'data': {'choices': [{'content': MOCK_ANSWER}]}}

            pipelines = create_pipelines('chatglm')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    def test_ernie(self):

        class MockRequest:
            def json(self):
                return {'result': MOCK_ANSWER}

        with patch('requests.request') as mock_llm:

            mock_llm.return_value = MockRequest()

            pipelines = create_pipelines('ernie')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    def test_dashscope(self):
        from http import HTTPStatus

        class MockRequest:
            @property
            def status_code(self):
                return HTTPStatus.OK

            @property
            def output(self):
                return {'text': MOCK_ANSWER}

        with patch('dashscope.Generation.call') as mock_llm:

            mock_llm.return_value = MockRequest()

            pipelines = create_pipelines('dashscope')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    def test_minimax(self):

        class MockRequest:
            def json(self):
                return {'reply': MOCK_ANSWER}

        with patch('requests.post') as mock_llm:

            mock_llm.return_value = MockRequest()

            pipelines = create_pipelines('minimax')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    def test_skychat(self):

        class MockRequest:
            def iter_lines(self):
                return [json.dumps({'code': 200, 'resp_data': {'reply': MOCK_ANSWER}}).encode('utf-8')]

        with patch('requests.post') as mock_llm:
            os.environ['SKYCHAT_APP_KEY'] = ''
            os.environ['SKYCHAT_APP_SECRET'] = ''

            mock_llm.return_value = MockRequest()

            pipelines = create_pipelines('skychat')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    def test_dolly(self):
        class MockDolly:
            def __call__(self, *args, **kwargs):
                return [{'generated_text': MOCK_ANSWER}]

        with patch('transformers.pipeline') as mock_llm:

            mock_llm.return_value = MockDolly()

            pipelines = create_pipelines('dolly')

            # Check attributes
            assert isinstance(pipelines, BasePipelines)
            assert hasattr(pipelines, 'insert_pipeline')
            assert hasattr(pipelines, 'search_pipeline')
            assert hasattr(pipelines, 'create')
            assert hasattr(pipelines, 'drop')
            assert hasattr(pipelines, 'check')
            assert hasattr(pipelines, 'count_entities')

            project = 'akcio_ut'
            data_src = 'https://github.com/towhee-io/towhee/blob/main/requirements.txt'
            question = 'test question'

            # Check insert
            if pipelines.check(project):
                pipelines.drop(project)

            assert not pipelines.check(project)
            pipelines.create(project)
            assert pipelines.check(project)

            insert_pipeline = pipelines.insert_pipeline
            res = insert_pipeline(data_src, project).to_list()
            num = pipelines.count_entities(project)
            assert len(res) <= num

            # Check search
            search_pipeline = pipelines.search_pipeline
            res = search_pipeline(question, [], project)
            final_answer = res.get()[0]
            assert final_answer == MOCK_ANSWER

            # Drop
            pipelines.drop(project)
            assert not pipelines.check(project)

    @classmethod
    def tearDownClass(cls):
        default_server.stop()
        default_server.cleanup()


if __name__ == '__main__':
    unittest.main()
