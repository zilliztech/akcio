import os
import sys
import unittest

from langchain.schema import AgentAction, AgentFinish

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from src_langchain.agent.prompt import FORMAT_INSTRUCTIONS
from src_langchain.agent.output_parser import OutputParser


class TestOutputParser(unittest.TestCase):
    output_parser = OutputParser()

    def test_get_format_instructions(self):
        assert FORMAT_INSTRUCTIONS == self.output_parser.get_format_instructions()

    def test_parse(self):
        action_name = 'mock_action'
        action_input = 'mock_action_input'
        text = '''
        ```json
        {
          "action": "mock_action",
          "action_input": "mock_action_input"
        }
        '''
        output = self.output_parser.parse(text)
        assert AgentAction(action_name, action_input, text) == output

    def test_parse_exception(self):
        action_input = 'mock_action_input'
        text = action_input
        output = self.output_parser.parse(text)
        json_text = '{\n ' + f'   "action": "Final Answer",\n    "action_input": "{action_input}"\n' + '}'
        assert AgentFinish({'output': action_input}, json_text) == output


if __name__ == '__main__':
    unittest.main()
