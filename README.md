# Akcio: Chat with Knowledge

- [Overview](#overview)
- [Deployment](#deployment)
    - [Option 1: Docker Image](#option-1-docker-image)
    - [Option 2: Source Code](#option-2-source-code)
- [Load Data](#load-data)

Play online:

- product: [OSSChat](osschat.io)
- demo: [HuggingFace Space] Coming soon ...

![gradio_ui](pics/gradio_ui.png)

## Overview

![overview](pics/osschat.png)

### Modules

- [Agent](./agent)
    - ChatAgent
    - Other agents (todo)
- [LLM](./llm)
    - ChatAI
    - QuestionGenerator (todo)
    - QueryModifier (todo)
- [Embedding](./embedding/)
    - TextEncoder
    - Other encoders (todo)
- [Store](./store)
    - VectorStore
    - MemoryStore
    - Other stores (todo)
- [DataLoader](./data_loader/)

## Deployment

### Option 1: Docker Image

Coming soon ...

### Option 2: Source Code

1. Downloads
    ```shell
    $ git clone https://github.com/jaelgu/akcio.git
    $ cd akcio
    ```

2. Install dependencies
    ```shell
    $ pip -r requirements.txt
    ```

3. Configure modules
    - Agent

        The default ChatAgent is based on Langchain ConversationChatAgent, using [customized prompts](agent/prompt.py).
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

    - LLM

        The default ChatAI module uses OpenAI service, which requires an [OpenAI API key](https://platform.openai.com/account/api-keys).
        Skip this step for a customized system not using OpenAI.

        ```shell
        $ export OPENAI_API_KEY=your_keys_here
        ```
        
    - Embedding

        By default, the embedding module uses Langchain HuggingFaceEmbeddings to convert text inputs to vectors. Modify [embedding configs](embedding/config.py) to configure it, like changing models or disable normalization:

        ```python
        # Text embedding
        textencoder_config = {
            'model': 'multi-qa-mpnet-base-cos-v1',
            'norm': True
        }
        ```

    - Store

        - Vector Store: You need to prepare the service of vector database in advance. For example, you can refer to [Milvus Documents](https://milvus.io/docs) or [Zilliz Cloud](https://zilliz.com/doc/quick_start) to learn about how to start a Milvus service.
        - Memory Store: You need to prepare the database for memory storage as well. By default, the memory store uses [Postgresql](https://www.postgresqltutorial.com) which requires installation.

        You can configure both stores via [config.py](store/config.py):
        ```python
        # Vector db configs
        vectordb_config = {
            'host': 'localhost',
            'port': 19530,
            'top_k': 10,
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

    ![fastapi](pics/fastapi.png)

    > `/`: Check service status
    >
    > `/answer`: Generate answer for the given question, with assigned session_id and project
    >
    > `/project/add`: Add data to project (will create the project if not exist)
    >
    > `/project/drop`: Drop project including delete data in both vector and memory storages.


## Load data

### Step 1. Download or crawl (optional)**

If you need download or crawl data from Internet, refer to [spider-nest]().  

If you want to load local files, skip this step.


### Step 2. Load project data

There are 3 options to load project data:

**Option 1. Online Service**

When the [FastAPI service](#deployment) is up, you can use the POST request `http://localhost:8900/project/add` to load data.

Parameters:
```json
{
  "project": "project_name",
  "data_src": "path/to/data"
}
```

This method is only recommended to load a small amount of data, but **not for a large amount of data**.

**Option 2. Command line**

Coming soon ...
