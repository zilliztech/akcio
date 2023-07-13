from typing import Mapping, Any, List, Optional, Tuple, Dict
import requests
import json
import os
import sys

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult, HumanMessage, AIMessage, SystemMessage, ChatMessage, ChatGeneration

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import CHAT_CONFIG

CHAT_CONFIG = CHAT_CONFIG['ernie']
llm_kwargs = CHAT_CONFIG.get('llm_kwargs', {})


class ChatLLM(BaseChatModel):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''
    api_key: str = CHAT_CONFIG['ernie_api_key']
    secret_key: str = CHAT_CONFIG['ernie_secret_key']
    temperature: float = llm_kwargs.get('temperature', 0)
    max_tokens: Optional[int] = llm_kwargs.get('max_tokens', None)
    n: int = llm_kwargs.get('n', 1)

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None) -> ChatResult:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params["messages"] = message_dicts
        payload = json.dumps(params)
        headers = {
            "Content-Type": "application/json"
        }

        url = self._create_url()
        response = requests.request(
            "POST", url, headers=headers, data=payload)
        return self._create_chat_result(response)

    def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None) -> ChatResult:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params["messages"] = message_dicts
        payload = json.dumps(params)
        headers = {
            "Content-Type": "application/json"
        }
        url = self._create_url()
        response = requests.request(
            "POST", url, headers=headers, data=payload)
        return self._create_chat_result(response)

    def _create_url(self):
        access_token = self._get_access_token(
            api_key=self.api_key, secret_key=self.secret_key)
        url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=' \
            + access_token
        return url

    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params: Dict[str, Any] = {**self._default_params}
        if stop is not None:
            if "stop" in params:
                raise ValueError(
                    "`stop` found in both the input and default params.")
            params["stop"] = stop
        message_dicts = []
        for m in messages:
            message_dicts.append(self._convert_message_to_dict(m))
            if isinstance(m, SystemMessage):
                message_dicts.append(
                    {"role": "assistant", "content": "OK."}
                )
        return message_dicts, params

    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        generations = []
        response = response.json()
        if "result" not in response:
            raise RuntimeError(response)
        message = self._convert_dict_to_message({"role": "assistant", "content": response["result"]})
        gen = ChatGeneration(message=message)
        generations.append(gen)
        llm_output = {
            "token_usage": response["usage"], "model_name": "ernie"}
        return ChatResult(generations=generations, llm_output=llm_output)

    @staticmethod
    def _convert_message_to_dict(message: BaseMessage) -> dict:
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, HumanMessage) or isinstance(message, SystemMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "assistant", "content": message.content}
        else:
            raise ValueError(f"Got unknown type {message}")
        if "name" in message.additional_kwargs:
            message_dict["name"] = message.additional_kwargs["name"]
        return message_dict
    
    @staticmethod
    def _convert_dict_to_message(_dict: dict) -> BaseMessage:
        role = _dict["role"]
        if role == "user":
            return HumanMessage(content=_dict["content"])
        elif role == "assistant":
            return AIMessage(content=_dict["content"])
        elif role == "system":
            return SystemMessage(content=_dict["content"])
        else:
            return ChatMessage(content=_dict["content"], role=role)

    @staticmethod
    def _get_access_token(api_key, secret_key):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key
        }
        return str(requests.post(url, params=params).json().get("access_token"))

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            "max_tokens": self.max_tokens,
            "n": self.n,
            "temperature": self.temperature,
        }


# if __name__ == '__main__':
#     chat = ChatLLM()
#     messages = [HumanMessage(content='Translate this sentence from English to French. I love programming.')]
#     ans = chat(messages)
#     print(type(ans), ans)
