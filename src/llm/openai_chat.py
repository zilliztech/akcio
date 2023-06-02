from typing import Optional, Union, Tuple

from langchain.chat_models import ChatOpenAI

from .config import chatllm_configs


class ChatLLM(ChatOpenAI):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''
    model_name: str = chatllm_configs.get('model_name', 'gpt-3.5-turbo')
    temperature: float = chatllm_configs.get('temperature', 0.0)
    openai_api_key: Optional[str] = chatllm_configs.get('openai_api_key', None)
    openai_organization: Optional[str] = chatllm_configs.get('openai_organization', None)
    request_timeout: Optional[Union[float, Tuple[float, float]]] = chatllm_configs.get('request_timeout', None)
    max_retries: int = chatllm_configs.get('max_retries', 3)
    streaming: bool = chatllm_configs.get('streaming', False)
    n: int = chatllm_configs.get('n', 1)
    max_tokens: Optional[int] = chatllm_configs.get('max_tokens', None)
