# Agent

An agent assembles modules together to create a workflow for some specific task. It normally uses llm to determine actions and procedures via prompts.

## ChatAgent
ChatAgent is able to build a chat system with action options from given tools such as doc retrieval through vector store. It also accepts llm and memory modules as parameters to enable more flexibility.

### Configuration

The default ChatAgent is based on LangChain `ConversationChatAgent`, using [customized prompts](agent/prompt.py).
 You can modify prompts for your scenarios.

```python
# Set system prompt
PREFIX = """Your system prompt goes here."""

# Define response format in user message
FORMAT_INSTRUCTIONS = """Your instructions for format response here."""

# Pass tools like search in user message
SUFFIX = """Your method to pass tools like search here."""

# Pass search results in user message
TEMPLATE_TOOL_RESPONSE = """Your method to pass search results and query here."""
```


### Example Usage

```python
from chat_agent import ChatAgent

# Define tools
tools = [
    Tool(
        name='Test',
        func=lambda x: 'This is a test tool.',
        description='Test action'
    )
]

# Define an agent
agent = ChatAgent.from_llm_and_tools(
    llm=chat_llm,
    tools=tools)

# Define a chain
agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=False
    )

# Run a test
final_answer = agent_chain.run(input='Test question')
```

### Customize Modules

- To customize ChatAgent, you can modify its methods in [chat_agent.py](chat_agent.py).

- To change output parser, you can modify [OutputParser](output_parser.py).
