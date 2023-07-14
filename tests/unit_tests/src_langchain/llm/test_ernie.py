import os
import sys
import unittest
from unittest.mock import patch

from langchain.schema import HumanMessage
from requests import Response

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))


class TestERNIE(unittest.TestCase):
    def test_generate(self):
        with patch('requests.post') as mock_post, patch('requests.request') as mock_request:
            mock_res1 = Response()
            mock_res1._content = b'{ "access_token" : "mock_token" }'
            mock_res2 = Response()
            mock_res2._content = b'{ "result" : "mock answer", "usage" : 2 }'
            mock_post.return_value = mock_res1
            mock_request.return_value = mock_res2
            from src_langchain.llm.ernie import ChatLLM

            chat_llm = ChatLLM(api_key='mock-key', secret_key='mock-key')
            messages = [HumanMessage(content='hello')]
            res = chat_llm._generate(messages)
            self.assertEqual(res.generations[0].text, 'mock answer')


if __name__ == '__main__':
    unittest.main()
