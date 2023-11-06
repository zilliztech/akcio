# LLM

LLM is the key component to ensure the functionality of chatbot. Besides providing AI response for users, it can also help to analyze the underlying user needs based on context or assume potential user questions given document.

## ChatLLM

The chatbot uses `ChatLLM` module to generate responses as the final answer, which will be returned to the user end. In order to adapt the LangChain agent, this must be a LangChain `BaseChatModel`.

By default, it uses `ChatLiteLLM` from LangChain, which calls the chat service of OpenAI (and Can support 50+ LLMs including Anthropic, Cohere, Google Palm, Replicate, Llama2 )
See ChatLiteLLM usage https://python.langchain.com/docs/integrations/chat/litellm

Refer to [LangChain Models](https://python.langchain.com/en/latest/modules/models.html) for more LLM options.

### Configuration

You can modify [config.py](../../config.py) to configure the ChatAI used to build the chat agent.
By default, it calls OpenAI Chat service using GPT-3.5 model and sets temperature to 0.
You can find more parameters at [OpenAI API Reference](https://platform.openai.com/docs/api-reference/chat).

```python
chat_configs = {
    'openai': {
        'openai_model': 'gpt-3.5-turbo',
        'openai_api_key': None,  # will use environment  value 'OPENAI_API_KEY' if None
        'llm_kwargs': {
            'temperature': 0.8,
            # 'max_tokens': 200,
            }
    },
    }
```

### Usage Example

```python
from langchain.schema import HumanMessage

from llm import ChatLLM

llm = ChatLLM(temperature=0.0)
messages = [HumanMessage(content='This is a test user message.')]
resp = llm(messages)
```

### Customization

A ChatLLM should inherit LangChain BaseChatModel.
To customize the module, you can define your own `_generate` and `_agenerate` methods.

```python
from typing import List, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain.schema import BaseMessage, ChatResult


class ChatLLM(BaseChatModel):
    def _generate(self,
                  messages: List[BaseMessage],
                  stop: Optional[List[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None
                  ) -> ChatResult:
                  # Your method here
                  pass
    
    async def _agenerate(self,
                         messages: List[BaseMessage],
                         stop: Optional[List[str]] = None,
                         run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
                         ) -> ChatResult:
                         # Your method here
                         pass
```
