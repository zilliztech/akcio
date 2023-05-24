from typing import Optional, Union, Tuple

from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import ChatOpenAI

from .config import chatai_configs


class ChatAI(ChatOpenAI):
    '''Chat with LLM given context. Must be a Langchain BaseLanguageModel to adapt agent.'''
    model_name: str = chatai_configs.get('model_name', 'gpt-3.5-turbo')
    temperature: float = chatai_configs.get('temperature', 0.0)
    openai_api_key: Optional[str] = chatai_configs.get('openai_api_key', None)
    openai_organization: Optional[str] = chatai_configs.get('openai_organization', None)
    request_timeout: Optional[Union[float, Tuple[float, float]]] = chatai_configs.get('request_timeout', None)
    max_retries: int = chatai_configs.get('max_retries', 3)
    streaming: bool = chatai_configs.get('streaming', False)
    n: int = chatai_configs.get('n', 1)
    max_tokens: Optional[int] = chatai_configs.get('max_tokens', None)
