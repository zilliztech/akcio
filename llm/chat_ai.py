from typing import List, Optional
from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun, Callbacks

from langchain.chat_models.base import BaseChatModel

from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, ChatResult


class ChatAI(ChatOpenAI):
    '''Chat with LLM given context. Must be a Langchain BaseLanguageModel to adapt agent.'''
    def __init__(self, *args, **kwargs):
        assert isinstance(self, BaseChatModel)  # llm should be a Langchain BaseLanguageModel
        super().__init__(*args, **kwargs)


# class ChatAI(BaseChatModel):
#     '''Customize LLM.'''
#     def _generate(self,
#                   messages: List[BaseMessage],
#                   stop: Optional[List[str]] = None,
#                   run_manager: Optional[CallbackManagerForLLMRun] = None
#                   ) -> ChatResult:
#         return super()._generate(messages, stop, run_manager)
    
#     async def _agenerate(
#             self,
#             messages: List[BaseMessage],
#             stop: Optional[List[str]] = None,
#             run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
#             ) -> ChatResult:
#          return await super()._agenerate(messages, stop, run_manager)