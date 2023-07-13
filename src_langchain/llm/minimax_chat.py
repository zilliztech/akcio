import sys
import os
from typing import Mapping, Any, List, Optional

import requests

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult, SystemMessage, HumanMessage, AIMessage, ChatGeneration

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import CHAT_CONFIG

CHAT_CONFIG = CHAT_CONFIG['minimax']
llm_kwargs = CHAT_CONFIG.get('llm_kwargs', {})


class ChatLLM(BaseChatModel):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''

    model_name: str = CHAT_CONFIG['minimax_model']
    api_key: str = CHAT_CONFIG['minimax_api_key'] or os.getenv('MINIMAX_API_KEY')
    group_id: str = CHAT_CONFIG['minimax_group_id'] or os.getenv('MINIMAX_GROUP_ID')
    llm_kwargs: dict = llm_kwargs

    url = f'https://api.minimax.chat/v1/text/chatcompletion?GroupId={group_id}'
    
    def _generate(self, messages: List[BaseMessage],
                  stop: Optional[List[str]] = None,
                  run_manager: Optional[Any] = None,
                  **kwargs: Any
                  ) -> ChatResult:
        payload = kwargs
        payload.update(self.llm_kwargs)
        system_message, messages = self._parse_inputs(messages)
        payload.update({
            'model': self.model_name,
            'messages': messages
        })
        if system_message:
            payload.update({
                'prompt': system_message,
                'role_meta': {
                    'user_name': 'Me',
                    'bot_name': 'Bot'
                },
            })
    
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        resp = requests.post(self.url, headers=headers, json=payload).json()
    
        return self._create_chat_result(resp)

    def _agenerate(self,
                   messages: List[BaseMessage],
                   stop: Optional[List[str]] = None,
                   run_manager: Optional[Any] = None,
                   **kwargs: Any
                   ) -> ChatResult:
        payload = kwargs
        payload.update(self.llm_kwargs)
        system_message, messages = self._parse_inputs(messages)
        payload.update({
            'model': self.model_name,
            'messages': messages
        })
        if system_message:
            payload.update({
                'prompt': system_message,
                'role_meta': {
                    'user_name': 'Me',
                    'bot_name': 'Bot'
                },
            })
    
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        resp = requests.post(self.url, headers=headers, json=payload).json()
    
        return self._create_chat_result(resp)


    def _parse_inputs(self, messages: List[BaseMessage]):
        new_messages = []
        system_message = None
        for m in messages:
            if isinstance(m, SystemMessage):
                system_message = m.content
            elif isinstance(m, HumanMessage):
                new_m = {'sender_type': 'USER', 'text': m.content}
                new_messages.append(new_m)
            elif isinstance(m, AIMessage):
                new_m = {'sender_type': 'BOT', 'text': m.content}
                new_messages.append(new_m)
            else:
                raise ValueError(f'Invalid message type: {type(m)}. \
                                 Only accept LangChain SystemMessage, AIMessage, or HumanMessage.')

        return system_message, new_messages

    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        message = AIMessage(content=response['reply'])
        gen = ChatGeneration(message=message)
        generations = [gen]
        return ChatResult(generations=generations)
    
    def _llm_type(self) -> str:
        return 'minimax'


# if __name__ == '__main__':
#     chat = ChatLLM()
#     messages = [HumanMessage(content='Translate this sentence from English to French. I love programming.')]
#     ans = chat(messages)
#     print(type(ans), ans)
