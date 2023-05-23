
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import ChatOpenAI

class ChatAI(ChatOpenAI):
    '''Chat with LLM given context. Must be a Langchain BaseLanguageModel to adapt agent.'''
    def __init__(self, *args, **kwargs):
        assert isinstance(self, BaseChatModel)  # llm should be a Langchain BaseLanguageModel
        super().__init__(*args, **kwargs)
