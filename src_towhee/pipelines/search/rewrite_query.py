import sys
import os
from towhee import AutoPipes, pipe

from pipelines.search import REWRITE_TEMP

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import get_llm_op  # pylint: disable=C0413


def build_prompt(question: str, history: list = []):  # pylint: disable=W0102
    if not history:
        history_str = ''
    output_str = ''
    for qa in history:
        output_str += f'Q: {qa[0]}\n'
        output_str += f'A: {qa[1]}\n'
    history_str = output_str.strip()
    prompt = REWRITE_TEMP.format(question=question, history_str=history_str)
    return [({'question': prompt})]

def parse_raw_ret(raw_ret, question):
    try:
        new_question = raw_ret.split('=> OUTPUT QUESTION: ')[1]
    except:  # pylint: disable=W0702
        new_question = question
    return new_question

def custom_pipeline(config):
    llm_op = get_llm_op(config)
    chat = AutoPipes.pipeline('osschat-search', config=config)
    p = (
        pipe.input('question', 'history', 'project')
            .map(('question', 'history'), 'prompt', build_prompt)
            .map('prompt', 'new_question', llm_op)
            .map(('new_question', 'question'), 'new_question', parse_raw_ret)
            .map(('new_question', 'history', 'project'), 'answer', chat)
            .output('new_question', 'answer')
    )
    return p
