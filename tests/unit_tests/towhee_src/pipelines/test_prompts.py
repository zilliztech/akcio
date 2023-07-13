import unittest

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from towhee_src.pipelines.prompts import PROMPT_OP, QUERY_PROMPT, SYSTEM_PROMPT


class TestPrompts(unittest.TestCase):
    def test_system_prompt(self):
        assert isinstance(SYSTEM_PROMPT, str)

    def test_query_prompt(self):
        query = QUERY_PROMPT.format(question='test question', context='test context')
        assert isinstance(query, str)

    def test_prompt_op(self):
        messages = PROMPT_OP('test question', 'test context', [])
        assert isinstance(messages, list)
        for m in messages:
            assert isinstance(m, dict)
            for k, v in m.items():
                assert k in ['system', 'question', 'answer']
                assert isinstance(v, str)
        assert 'question' in messages[-1] and 'answer' not in messages[-1]


if __name__== '__main__':
    unittest.main()