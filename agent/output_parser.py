from typing import Union
from langchain.agents.conversational_chat.output_parser import ConvoOutputParser
from langchain.schema import AgentAction, AgentFinish

from .prompt import FORMAT_INSTRUCTIONS


class OutputParser(ConvoOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS
    
    def parse(self, text: str)  -> Union[AgentAction, AgentFinish]:
        '''Customize parse method here'''
        return super().parse(text)