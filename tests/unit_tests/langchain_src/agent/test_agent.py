import os
import sys
import unittest

from langchain.agents import AgentExecutor, Tool
from langchain.llms.fake import FakeListLLM

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from langchain_src.agent import ChatAgent


class TestChatAgent(unittest.TestCase):
    tools = [
        Tool(
            name='Python REPL',
            func=lambda x: '4',  # mock result when executing 'print(2 + 2)'
            description='Useful when you need to run python code in the REPL.',
        )
    ]
    responses = ['''```json\n{"action": "Python REPL",\n"action_input": "print(2 + 2)"}''', "Final Answer: 4"]
    llm = FakeListLLM(responses=responses)
    chat_agent = ChatAgent.from_llm_and_tools(llm=llm, tools=tools)

    def test_run_chat_agent(self):
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.chat_agent,
            tools=self.tools,
            verbose=False
        )
        final_answer = agent_executor.run(input='whats 2 + 2', chat_history=[])
        assert final_answer == self.responses[1]


if __name__ == '__main__':
    unittest.main()
