from typing import Mapping, Any

import torch
from transformers import pipeline

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult, HumanMessage, AIMessage, ChatGeneration


class ChatLLM(BaseChatModel):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''

    model_name: str = 'databricks/dolly-v2-3b'
    device: str = 'auto'

    generate_text = pipeline(
        model=model_name, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map=device)

    def _generate(self, messages: List[BaseMessage]) -> ChatResult:
        prompt = self._create_prompt(messages)
        resp = self.generate_text(prompt)
        return self._create_chat_result(resp)

    def _agenerate(self, messages: List[BaseMessage]) -> ChatResult:
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


# if __name__ == '__main__':
#     chat = ChatLLM()
#     messages = [HumanMessage(content='Translate this sentence from English to French. I love programming.')]
#     ans = chat(messages)
#     print(type(ans), ans)
