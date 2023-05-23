# LLM

LLM is the key component to ensure the functionality of chatbot. Besides providing AI response for users, it can also help to analyze the underlying user needs based on context or assume potential user questions given document.

## ChatAI

The chatbot uses `ChatAI` module to generate responses as the final answer, which will be returned to the user end. In order to adapt the Langchain agent, this must be a Langchain `BaseChatModel`.

By default, it uses `ChatOpenAI` from Langchain, which calls the chat service of OpenAI.
Refer to [Langchain Models](https://python.langchain.com/en/latest/modules/models.html) for more LLM Yoptions.

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

## QueryModifier

Todo