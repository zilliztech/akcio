# LLM

LLM is the key component to ensure the functionality of chatbot. Besides providing AI response for users, it can also help to analyze the underlying user needs based on context or assume potential user questions given document.

## ChatAI

The chatbot uses `ChatAI` module to generate responses as the final answer, which will be returned to the user end. In order to adapt the Langchain agent, this must be a Langchain `BaseLanguageModel`.

By default, it uses `ChatOpenAI` from Langchain, which calls the chat service of OpenAI.
Refer to [Langchain Models](https://python.langchain.com/en/latest/modules/models.html) for more LLM Yoptions.


You can also customize `ChatAI` by modifying `chat_ai.py`:

```python
from langchain.base_language import BaseLanguageModel
from langchain.schema import LLMResult, PromptValue


def test_model(prompts):
    return "test answer"

class ChatAI(BaseLanguageModel):
    def generate_prompt(
        self,
        prompts: List[PromptValue]
    ) -> LLMResult:
        """Take in a list of prompt values and return an LLMResult."""
        output = self.agenerate_prompt(prompts=prompts)
        return output

    async def agenerate_prompt(
        self,
        prompts: List[PromptValue]
    ) -> LLMResult:
        llm_output = test_model(prompts)
        output = LLMResult(generations=generations, llm_output=llm_output)
        return output
```

## QuestionGenerator

Todo

## QueryModifier

Todo