import os
import sys
import unittest
from unittest.mock import patch
from langchain.schema import HumanMessage, AIMessage

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))


class TestERNIE(unittest.TestCase):
    def test_generate(self):
        from erniebot.response import EBResponse
        with patch('erniebot.ChatCompletion.create') as mock_post:
            mock_res = EBResponse(rcode=200,
                                  rbody={'id': 'as-0000000000', 'object': 'chat.completion', 'created': 11111111,
                                        'result': 'OK, this is a mock answer.',
                                        'usage': {'prompt_tokens': 1, 'completion_tokens': 13, 'total_tokens': 14},
                                        'need_clear_history': False, 'is_truncated': False},
                                  rheaders={'Connection': 'keep-alive',
                                           'Content-Security-Policy': 'frame-ancestors https://*.baidu.com/',
                                           'Content-Type': 'application/json', 'Date': 'Mon, 23 Oct 2023 03:30:53 GMT',
                                           'Server': 'nginx', 'Statement': 'AI-generated',
                                           'Vary': 'Origin, Access-Control-Request-Method, Access-Control-Request-Headers',
                                           'X-Frame-Options': 'allow-from https://*.baidu.com/',
                                           'X-Request-Id': '0' * 32,
                                           'Transfer-Encoding': 'chunked'}
                                  )
            mock_post.return_value = mock_res

            from src_langchain.llm.ernie import ChatLLM

            EB_API_TYPE = 'mock_type'
            EB_ACCESS_TOKEN = 'mock_token'

            chat_llm = ChatLLM(eb_api_type=EB_API_TYPE, eb_access_token=EB_ACCESS_TOKEN)
            messages = [
                HumanMessage(content='hello'),
                AIMessage(content='hello, can I help you?'),
                HumanMessage(content='Please give me a mock answer.'),
            ]
            res = chat_llm._generate(messages)
            self.assertEqual(res.generations[0].text, 'OK, this is a mock answer.')


if __name__ == '__main__':
    unittest.main()
