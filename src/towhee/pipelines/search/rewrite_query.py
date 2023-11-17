import sys
import os
from towhee import AutoPipes, pipe

from pipelines.search import REWRITE_TEMP

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import get_llm_op  # pylint: disable=C0413

ZH_PRONOUN_LIST = ['他', '她', '它', '者', '这', ]

EN_PRONOUN_LIST = ['he', 'his', 'him', 'she', 'her', 'it', 'they', 'them', 'their', 'both', 'former', 'latter',
                   'this', 'these', 'that']

PRONOUN_LIST = ZH_PRONOUN_LIST + EN_PRONOUN_LIST


class RewriteQuery:
    '''
    Replace third-person pronouns with words from historical dialogue
    '''

    def __init__(self, config):
        self._llm_op = get_llm_op(config)

    def __call__(self, question: str, history: list = []):  # pylint: disable=W0102
        if self._contain_pron(question):
            prompt = self._build_prompt(question, history)
            raw_ret = self._llm_op(prompt)
            new_question = self._parse_raw_ret(raw_ret, question)
            return new_question
        else:
            return question

    def _contain_pron(self, question: str):
        for pron in PRONOUN_LIST:
            if pron in question.lower():
                return True
        return False

    def _build_prompt(self, question: str, history: list = []):  # pylint: disable=W0102
        output_str = ''
        for qa in history:
            output_str += f'Q: {qa[0]}\n'
            output_str += f'A: {qa[1]}\n'
        history_str = output_str.strip()
        prompt = REWRITE_TEMP.format(question=question, history_str=history_str)
        return [({'question': prompt})]

    def _parse_raw_ret(self, raw_ret: str, question: str):
        try:
            raw_ret = raw_ret.replace('&gt;', '>')
            new_question = raw_ret.split('=> OUTPUT QUESTION: ')[1].split('-------------------')[0]
        except:  # pylint: disable=W0702
            new_question = question
        return new_question


def custom_pipeline(config):
    chat = AutoPipes.pipeline('osschat-search', config=config)
    p = (
        pipe.input('question', 'history', 'project')
            .map(('question', 'history'), 'new_question', RewriteQuery(config))
            .map(('new_question', 'history', 'project'), 'answer', chat)
            .output('new_question', 'answer')
    )
    return p
