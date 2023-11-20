from config import LLM_OPTION  # pylint: disable=C0413
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


if LLM_OPTION == 'openai':
    from .openai_chat import ChatLLM
elif LLM_OPTION == 'dolly':
    from .dolly_chat import ChatLLM
elif LLM_OPTION == 'ernie':
    from .ernie import ChatLLM
elif LLM_OPTION == 'minimax':
    from .minimax_chat import ChatLLM
else:
    raise RuntimeError(
        f'LangChain mode has not supported the LLM option yet: {LLM_OPTION}.')
