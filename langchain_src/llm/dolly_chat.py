import sys
import os
from typing import Mapping, Any, List, Optional

import torch
from transformers import pipeline

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult, HumanMessage, AIMessage, ChatGeneration

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import CHAT_CONFIG

CHAT_CONFIG = CHAT_CONFIG['dolly']
llm_kwargs = CHAT_CONFIG.get('llm_kwargs', {})


class ChatLLM(BaseChatModel):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''

    model_name: str = CHAT_CONFIG['dolly_model']
    device: str = llm_kwargs.get('device', 'auto')

    generate_text = pipeline(
        model=model_name, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map=device)

    def _generate(self,
                  messages: List[BaseMessage],
                  stop: Optional[List[str]] = None,
                  run_manager: Optional[Any] = None,
                  ) -> ChatResult:
        prompt = self._create_prompt(messages)
        resp = self.generate_text(prompt)
        return self._create_chat_result(resp)

    def _agenerate(self,
                   messages: List[BaseMessage],
                   stop: Optional[List[str]] = None,
                   run_manager: Optional[Any] = None,
                   ) -> ChatResult:
        prompt = self._create_prompt(messages)
        resp = self.generate_text(prompt)
        return self._create_chat_result(resp)

    def _create_prompt(self, messages: List[BaseMessage]):
        if isinstance(messages[-1], HumanMessage):
            prompt = messages[-1].content
        else:
            raise AttributeError('Unsupported message for Dolly.')
        return prompt

    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        message = AIMessage(content=response[0]['generated_text'])
        gen = ChatGeneration(message=message)
        generations = [gen]
        return ChatResult(generations=generations)
    
    def _llm_type(self) -> str:
        return 'dolly'


# if __name__ == '__main__':
#     chat = ChatLLM()
#     messages = [HumanMessage(content='Translate this sentence from English to French. I love programming.')]
#     ans = chat(messages)
#     print(type(ans), ans)
