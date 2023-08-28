import sys
import os
from towhee import AutoPipes, AutoConfig


def build_insert_pipeline(
        name: str = 'osschat-insert',
        config: object = AutoConfig.load_config('osschat-insert')
        ):
    try:
        insert_pipeline = AutoPipes.pipeline(name, config=config)
    except RuntimeError as e:  # pylint: disable=W0703
        if name.replace('-', '_') == 'generate_questions':
            sys.path.append(os.path.dirname(__file__))
            from generate_questions import custom_pipeline  # pylint: disable=c0415

            insert_pipeline = custom_pipeline(config=config)
        else:
            raise RuntimeError(e) from e
    return insert_pipeline
