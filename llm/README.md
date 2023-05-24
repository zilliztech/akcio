# LLM

LLM is the key component to ensure the functionality of chatbot. Besides providing AI response for users, it can also help to analyze the underlying user needs based on context or assume potential user questions given document.

## ChatAI

The chatbot uses `ChatAI` module to generate responses as the final answer, which will be returned to the user end. In order to adapt the Langchain agent, this must be a Langchain `BaseChatModel`.

By default, it uses `ChatOpenAI` from Langchain, which calls the chat service of OpenAI.
Refer to [Langchain Models](https://python.langchain.com/en/latest/modules/models.html) for more LLM options.

### Configuration

You can modify [config.py](./config.py) to configure the ChatAI used to build the chat agent.
By default, it calls OpenAI Chat service using GPT-3.5 model and sets temperature to 0.
You can find more parameters at [OpenAI API Reference](https://platform.openai.com/docs/api-reference/chat).

```python
chatai_configs = {
    'model_name': 'gpt-3.5-turbo',
    'temperature': 0,
    # 'openai_api_key':'your_openai_key_goes_here',  # will use enviornment variable if not set in configs
    # 'openai_organization': ‘your_organization_goes_here’,  # will use enviornment variable if not set in configs
    # 'request_timeout': 600,  # in seconds
    # 'max_retries': 3,
    # 'streaming': False,
    # 'n': 1,
    # 'max_tokens': 1000
}
```

### Usage Example

```python
from langchain.schema import HumanMessage

from chat_ai import ChatAI

llm = ChatAI(temperature=0.0)
messages = [HumanMessage(content='This is a test user message.')]
resp = llm(messages)
```

### Customization

You can customize `ChatAI` by modifying `chat_ai.py`:

```python
from typing import List, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain.schema import BaseMessage, ChatResult


class ChatAI(BaseChatModel):
    def _generate(self,
                  messages: List[BaseMessage],
                  stop: Optional[List[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None
                  ) -> ChatResult:
                  # Your method here
                  pass
    
    async def _agenerate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            ) -> ChatResult:
            # Your method here
            pass
```

## QuestionGenerator

Todo
