from typing import Any, List, Dict, Optional
import os
import sys

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult, HumanMessage, AIMessage, SystemMessage, ChatMessage, \
    ChatGeneration

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import CHAT_CONFIG  # pylint: disable=C0413


CHAT_CONFIG = CHAT_CONFIG['ernie']
llm_kwargs = CHAT_CONFIG.get('llm_kwargs', {})


class ChatLLM(BaseChatModel):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''
    model_name: str = CHAT_CONFIG['ernie_model']
    eb_api_type: str = CHAT_CONFIG['eb_api_type'] or os.getenv('EB_API_TYPE')
    eb_access_token: str = CHAT_CONFIG['eb_access_token'] or os.getenv('EB_ACCESS_TOKEN')
    llm_kwargs: dict = llm_kwargs

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None) -> ChatResult:  # pylint: disable=W0613
        import erniebot  # pylint: disable=C0415
        erniebot.api_type = self.eb_api_type
        erniebot.access_token = self.eb_access_token

        message_dicts = self._create_message_dicts(messages)

        response = erniebot.ChatCompletion.create(
            model=self.model_name,
            messages=message_dicts,
            **self.llm_kwargs
        )
        return self._create_chat_result(response)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None  # pylint: disable=W0613
    ) -> ChatResult:
        import erniebot  # pylint: disable=C0415
        erniebot.api_type = self.eb_api_type
        erniebot.access_token = self.eb_access_token

        message_dicts = self._create_message_dicts(messages)
        response = erniebot.ChatCompletion.create(
            model=self.model_name,
            messages=message_dicts,
            **self.llm_kwargs
        )
        return self._create_chat_result(response)

    def _create_message_dicts(
            self, messages: List[BaseMessage]
    ) -> List[Dict[str, Any]]:

        message_dicts = []
        for m in messages:
            m_dict = self._convert_message_to_dict(m)
            if m_dict:
                message_dicts.append(self._convert_message_to_dict(m))
        return message_dicts

    def _create_chat_result(self, response: 'EBResponse') -> ChatResult:
        generations = []
        response = response.to_dict()
        if 'result' not in response:
            raise RuntimeError(response)
        message = self._convert_dict_to_message(
            {'role': 'assistant', 'content': response['result']})
        gen = ChatGeneration(message=message)
        generations.append(gen)
        llm_output = {
            'token_usage': response['usage'], 'model_name': 'ernie'}
        return ChatResult(generations=generations, llm_output=llm_output)

    @staticmethod
    def _convert_message_to_dict(message: BaseMessage) -> dict:
        message_dict = {}
        if isinstance(message, ChatMessage):
            message_dict = {'role': message.role, 'content': message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {'role': 'user', 'content': message.content}
        elif isinstance(message, AIMessage):
            message_dict = {'role': 'assistant', 'content': message.content}
        if 'name' in message.additional_kwargs:
            message_dict['name'] = message.additional_kwargs['name']
        return message_dict

    @staticmethod
    def _convert_dict_to_message(_dict: dict) -> BaseMessage:  # pylint: disable=C0103
        role = _dict['role']
        if role == 'user':
            return HumanMessage(content=_dict['content'])
        elif role == 'assistant':
            return AIMessage(content=_dict['content'])
        elif role == 'system':
            return SystemMessage(content=_dict['content'])
        else:
            return ChatMessage(content=_dict['content'], role=role)

    @property
    def _llm_type(self) -> str:
        return 'ernie'
