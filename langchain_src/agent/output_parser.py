from typing import Union
import json
import re

from langchain.agents.conversational_chat.output_parser import ConvoOutputParser
from langchain.schema import AgentAction, AgentFinish

from .prompt import FORMAT_INSTRUCTIONS


class OutputParser(ConvoOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        try:
            return super().parse(text)
        except Exception:
            text = re.sub('\n', r'\\n', text)
            if '''"action": "Search"''' and '''"action_input":''' in text:
                text = text.split('''"action_input":''')[1].strip()
                json_text = '{\n ' + f'   "action": "Search",\n    "action_input": "{text}"\n' + '}'
            else:
                if '''"action_input":''' in text:
                    text = text.split('''"action_input":''')[1].strip()
                json_text = '{\n ' + f'   "action": "Final Answer",\n    "action_input": "{text}"\n' + '}'
            cleaned_output = json_text
            response = json.loads(cleaned_output)
            action, action_input = response['action'], response['action_input']
            if action == 'Final Answer':
                return AgentFinish({'output': action_input}, json_text)
            else:
                return AgentAction(action, action_input, json_text)
