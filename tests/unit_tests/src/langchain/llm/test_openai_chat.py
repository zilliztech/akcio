import unittest


class TestOpenAIChat(unittest.TestCase):
    def test_init(self):
        from src.langchain.llm.openai_chat import ChatLLM
        chat_llm = ChatLLM(openai_api_key='mock-key')
        self.assertEqual(chat_llm.__class__.__name__, 'ChatLLM')


if __name__ == '__main__':
    unittest.main()
