import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))


class TestOpenAIChat(unittest.TestCase):
    def test_init(self):
        from langchain_src.llm.openai_chat import ChatLLM
        chat_llm = ChatLLM(openai_api_key='mock-key')
        self.assertEqual(chat_llm.__class__.__name__, 'ChatLLM')


if __name__ == '__main__':
    unittest.main()
