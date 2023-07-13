from typing import Any, List, Optional, Sequence
from pydantic import Field

from langchain.agents.conversational_chat.prompt import PREFIX, SUFFIX
from langchain.callbacks.base import BaseCallbackManager
from langchain.agents import ConversationalChatAgent, AgentOutputParser, Agent
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseOutputParser, BaseLanguageModel
from langchain.tools.base import BaseTool

from .output_parser import OutputParser
from .prompt import PREFIX, SUFFIX, TEMPLATE_TOOL_RESPONSE


class ChatAgent(ConversationalChatAgent):
    '''Customize LangChain ConversationalChatAgent'''

    output_parser: AgentOutputParser = Field(default_factory=OutputParser)
    template_tool_response: str = TEMPLATE_TOOL_RESPONSE

    @classmethod
    def _get_default_output_parser(cls, **kwargs: Any) -> OutputParser:
        return OutputParser(**kwargs)

    @classmethod
    def from_llm_and_tools(cls,
                           llm: BaseLanguageModel,
                           tools: Sequence[BaseTool],
                           callback_manager: Optional[BaseCallbackManager] = None,
                           output_parser: Optional[BaseOutputParser] = OutputParser(),
                           system_message: str = PREFIX,
                           human_message: str = SUFFIX,
                           input_variables: Optional[List[str]] = None,
                           **kwargs: Any
                           ) -> Agent:
        return super().from_llm_and_tools(
            llm,
            tools,
            callback_manager,
            output_parser,
            system_message,
            human_message,
            input_variables,
            **kwargs
        )

    @classmethod
    def create_prompt(
            cls,
            tools: Sequence[BaseTool],
            system_message: str = PREFIX,
            human_message: str = SUFFIX,
            input_variables: Optional[List[str]] = None,
            output_parser: Optional[BaseOutputParser] = None) -> BasePromptTemplate:
        return super().create_prompt(tools, system_message, human_message, input_variables, output_parser)
