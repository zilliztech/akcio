import os
import sys
import unittest
from unittest.mock import patch

from langchain.schema import HumanMessage

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))

MOCK_ANSWER = 'mock answer'


class TestDollyChat(unittest.TestCase):
    def test_generate(self):
        class MockGenerateText:
            def __call__(self, prompt):
                return [{'generated_text': MOCK_ANSWER}]

        with patch('transformers.pipeline') as mock_pipelines:
            mock_pipelines.return_value = MockGenerateText()
            from langchain_src.llm.dolly_chat import ChatLLM

            chat_llm = ChatLLM(model_name='mock', device='cpu', )
            messages = [HumanMessage(content='hello')]
            res = chat_llm._generate(messages)
            self.assertEqual(res.generations[0].text, MOCK_ANSWER)


if __name__ == '__main__':
    unittest.main()
