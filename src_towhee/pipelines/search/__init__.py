import sys
import os
from towhee import AutoPipes, AutoConfig

sys.path.append(os.path.dirname(__file__))

from prompts import PROMPT_OP  # pylint: disable=C0413


def build_search_pipeline(
        name: str = 'osschat-search',
        config: object = AutoConfig.load_config('osschat-search')
        ):
    if PROMPT_OP:
        config.customize_prompt = PROMPT_OP
    try:
        search_pipeline = AutoPipes.pipeline(name, config=config)
    except Exception:  # pylint: disable=W0703
        if name.replace('-', '_') == 'rewrite_query':
            sys.path.append(os.path.dirname(__file__))
            from rewrite_query import custom_pipeline    # pylint: disable=c0415

            search_pipeline = custom_pipeline(config=config)
        else:
            raise AttributeError(f'Invalid query mode: {name}')  # pylint: disable=W0707
    return search_pipeline
