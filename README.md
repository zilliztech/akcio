# Akcio: Chat with Knowledge

- [Overview](#overview)
- [Deployment](#deployment)
    - [Option 1: Docker Image](#option-1-docker-image)
    - [Option 2: Source Code](#option-2-source-code)
- [Load Data](#load-data)

Play online:

<img src='pics/gradio_ui.png' width='75%' alignment='centre'>

- product: [OSSChat](osschat.io)
- demo: HuggingFace Space (coming soon ...)

## Overview

<img src='pics/osschat.png' width='75%' alignment='centre'>

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
        If you want to configure prompts or customize agent modules, refer to [agent](./agent) for guide.

    - LLM

        The default ChatAI module uses OpenAI service, which requires an [OpenAI API key](https://platform.openai.com/account/api-keys).
        Skip this step for a customized system not using OpenAI.

        ```shell
        $ export OPENAI_API_KEY=your_keys_here
        ```

        If you want to customize llm modules, you can refer to [llm](./llm) for guide.
        
    - Embedding

        By default, the embedding module uses Langchain HuggingFaceEmbeddings to convert text inputs to vectors.

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

    <img src='pics/fastapi.png' width='75%' alignment='centre'>

    > `/`: Check service status
    >
    > `/answer`: Generate answer for the given question, with assigned session_id and project
    >
    > `/project/add`: Add data to project (will create the project if not exist)
    >
    > `/project/drop`: Drop project including delete data in both vector and memory storages.


## Load data

The `insert` function in [operations](operations.py) loads project data from url(s) or file(s).

There are 2 options to load project data:

### Option 1: Offline

You can run python script below to load data:

```python
from operations import insert

# Insert data from file (use list of files as input for bulk insert)
insert(data_src='path/to/doc', project='project_name', source_type='file')

# Insert data from url (use list of urls as input for bulk insert)
insert(data_src='link/to/doc', project='project_name', source_type='url')
```

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
