import os
import sys
from typing import Optional

from langchain.chat_models import ChatOpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import CHAT_CONFIG  # pylint: disable=C0413

CHAT_CONFIG = CHAT_CONFIG['openai']
llm_kwargs = CHAT_CONFIG.get('llm_kwargs', {})


class ChatLLM(ChatOpenAI):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''
    model_name: str = CHAT_CONFIG.get('openai_model', 'gpt-3.5-turbo')
    openai_api_key: Optional[str] = CHAT_CONFIG.get('openai_api_key', None)
    temperature: float = llm_kwargs.get('temperature', 0.0)
    openai_organization: Optional[str] = llm_kwargs.get('openai_organization', None)
    streaming: bool = llm_kwargs.get('streaming', False)
    n: int = llm_kwargs.get('n', 1)
    max_tokens: Optional[int] = llm_kwargs.get('max_tokens', None)
