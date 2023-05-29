# Akcio: Enhancing LLM-Powered ChatBot with CVP Stack

[OSSChat](https://osschat.io) |
[Documents](https://github.com/zilliztech/akcio/wiki) |
[Contact](https://zilliz.com/contact-sales) |
[Liscense](#license)

Index

- [Overview](#overview)
- [Deployment](#deployment)
- [Load Data](#load-data)

ChatGPT has constraints due to its limited knowledge base, sometimes resulting in hallucinating answers when asked about unfamiliar topics. We are introducing the new AI stack, ChatGPT+Vector database+prompt-as-code, or the CVP Stack, to overcome this constraint.

We have built [OSSChat](https://osschat.io) as a working demonstration of the CVP stack. Now we are presenting the technology behind OSSChat in this repository with a code name of Akcio.

With this project, you are able to build a knowledge-enhanced ChatBot using LLM service like ChatGPT. 
By the end, you will learn how to start a backend service using FastAPI, which provides standby APIs to support further applications. Alternatively, we show how to use Gradio to build an online demo with user interface.

## Overview

The system is built on top of Langchain Agent using vector database for semantic search and memory storage for context support.

<img src='pics/osschat.png' width='75%' alignment='centre'>

### Modules

- [Agent](./src/agent)
    - ChatAgent
    - Other agents (todo)
- [LLM](./src/llm)
    - ChatAI
- [Embedding](./src/embedding/)
    - TextEncoder
    - Other encoders (todo)
- [Store](./src/store)
    - VectorStore
    - MemoryStore
    - Other stores (todo)
- [DataLoader](./src/data_loader/)
    - DataParser
    - QuestionGenerator

## Deployment

1. Downloads
    ```shell
    $ git clone https://github.com/zilliztech/akcio.git
    $ cd akcio
    ```

2. Install dependencies
    ```shell
    $ pip -r requirements.txt
    ```

3. Configure modules
    - Agent

        It will use default agents and prompts.
        If you want to configure prompts or customize agent modules, refer to [agent](./src/agent) for guide.

    - LLM

        The default ChatAI module uses OpenAI service, which requires an [OpenAI API key](https://platform.openai.com/account/api-keys).

        ```shell
        $ export OPENAI_API_KEY=your_keys_here
        ```

        If you want to customize llm modules, you can refer to [llm](./src/llm) for guide.
        
    - Embedding

        By default, the embedding module uses Langchain HuggingFaceEmbeddings to convert text inputs to vectors. Here are some information about the default embedding method:
        - model: [multi-qa-mpnet-base-cos-v1](https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-cos-v1)(420MB)
        - dim: 768
        - normalization: True

        If you want to customize embedding method, you can refer to [embedding](./src/embedding) for guide.

    - Store

        - Vector Store: You need to prepare the service of vector database in advance. For example, you can refer to [Milvus Documents](https://milvus.io/docs) or [Zilliz Cloud](https://zilliz.com/doc/quick_start) to learn about how to start a Milvus service.
        - Scalar Store (Optional): This is optional, only work when elastic is enabled in operation. To prepare the Elasticsearch service, you can refer to its [official document](https://www.elastic.co/).
        - Memory Store: You need to prepare the database for memory storage as well. By default, the memory store uses [Postgresql](https://www.postgresqltutorial.com) which requires installation.

        You can configure all stores via [config.py](./src/store/config.py), including set up connection arguments for each database:
        ```python
        # Vector db configs
        vectordb_config = {
            'host': 'localhost',
            'port': 19530,
            'top_k': 10,
        }

        # Scalar db configs (optional)
        scalardb_config = {
            'host': 'localhost',
            'port': 9200,
            # 'ca_certs': 'path/to/ca_certs',
            'user': 'elastic',
            'password': 'es_password_goes_here'
        }

        # Memory db configs
        memorydb_config = {
            'connect_str': 'postgresql://postgres:postgres@localhost/chat_history'
        }
        ```

4. Start service

    The main script will run a FastAPI service with default address `localhost:8900`.

    ```shell
    $ python main.py
    ```

4. Access via browser
    
    You can open url https://localhost:8900/docs in browser to access the web service.

    <img src='pics/fastapi.png' width='75%' alignment='centre'>

    > `/`: Check service status
    >
    > `/answer`: Generate answer for the given question, with assigned session_id and project
    >
    > `/project/add`: Add data to project (will create the project if not exist)
    >
    > `/project/drop`: Drop project including delete data in both vector and memory storages.


## Load data

The `insert` function in [operations](./src/operations.py) loads project data from url(s) or file(s).

There are 2 options to load project data:

### Option 1: Offline

We recommend this method, which loads data in separate steps.
There is also advanced options to load document with advanced options.
Refer to [offline_tools](./src/offline_tools) for instructions.

### Option 2. Online

When the [FastAPI service](#deployment) is up, you can use the POST request `http://localhost:8900/project/add` to load data.

Parameters:
```json
{
  "project": "project_name",
  "data_src": "path/to/data"
}
```

This method is only recommended to load a small amount of data, but **not for a large amount of data**.


<br />

---
## License
