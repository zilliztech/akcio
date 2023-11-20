import sys
import os
from towhee import AutoPipes, AutoConfig, ops

from config import LANGUAGE

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

if LANGUAGE == 'zh':
    from prompts.zh import REWRITE_TEMP, QUERY_PROMPT, SYSTEM_PROMPT  # pylint: disable=C0413,W0611
else:
    from prompts.en import REWRITE_TEMP, QUERY_PROMPT, SYSTEM_PROMPT  # pylint: disable=C0413,W0611

PROMPT_OP = ops.prompt.template(QUERY_PROMPT, ['question', 'context'], SYSTEM_PROMPT)

def build_search_pipeline(
        name: str = 'osschat-search',
        config: object = AutoConfig.load_config('osschat-search')
        ):

    config.customize_prompt = PROMPT_OP
    try:
        search_pipeline = AutoPipes.pipeline(name, config=config)
    except RuntimeError as e:  # pylint: disable=W0703
        if name.replace('-', '_') == 'rewrite_query':
            sys.path.append(os.path.dirname(__file__))
            from rewrite_query import custom_pipeline    # pylint: disable=c0415

            search_pipeline = custom_pipeline(config=config)
        else:
            raise RuntimeError(e) from e  # pylint: disable=W0707
    return search_pipeline
