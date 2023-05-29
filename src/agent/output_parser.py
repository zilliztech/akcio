from langchain.agents.conversational_chat.output_parser import ConvoOutputParser

from .prompt import FORMAT_INSTRUCTIONS


class OutputParser(ConvoOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    # def parse(self, text: str):
    #     '''Customize parse method here'''
    #     return super().parse(text)
