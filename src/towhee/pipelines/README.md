# Pipelines

## TowheePipelines

The `TowheePipelines` prepares insert and search pipeline for the system. It should have methods below to adapt operations in chatbot:

**Parameters:**

- `llm_src`: A string to indicate which llm service to use. Supported value:
    - openai
    - dolly
    - ernie
    - dashscope
    - minimax
    - chatglm
    - skychat

**Properties:**

- `search_pipeline`:
    A Towhee pipeline searches relevant information across the project knowledge for the user's query, and then passes both user query and retrieved documents to LLM service to generate the final answer.
- `insert_pipeline`:
    A Towhee pipeline firstly loads & splits data from source (URL or file path), and then save documents & corresponding data such as text embeddings in database(s).

By default, it uses [Zilliz Cloud or Milvus](https://www.zilliz.com) to store documents with embeddings.
If scalar store is enabled, it will use [Elastic](https://www.elastic.co) as default scalar store.
You can modify [config.py](../../config.py) to configure it.

## Prompt

- `SYSTEM_PROMPT`: The system message will be passed to LLM service.
- `QUERY_PROMPT`: The prompt template will be used to process a user's query.
- `PROMPT_OP`:

    The function to prepare messages for a LLM operator, which is used in search pipeline. By default, it is operator [prompt/template](https://towhee.io/prompt/template) applied with `SYSTEM_PROMPT` and `QUERY_PROMPT`. 
