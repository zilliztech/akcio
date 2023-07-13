# Store

## VectorStore

The `VectorStore` is storage of embeddings. It should follow API design below to adapt operations in chatbot:

**`VectorStore(table_name: str, embedding_func: Embeddings)`**

**Parameters:**

- `table_name (str)`: table name in vector database
- `embedding_func (Embeddings)`: embedding method to convert query or documents to vectors

**Methods:**

- `insert`: data insert, given a list of documents, returns how many data entities inserted
- `search`: semantic search, given a query in string, returns a list of useful documents

By default, it uses `Milvus` in LangChain. You can modify [config.py](../../config.py) to configure it.
The default module also works with [Zilliz Cloud](https://zilliz.com) by setting configurations for the vector store below:

```python
# Vector db configs
VECTORDB_CONFIG = {
    'connection_args': {
        'uri': os.getenv('MILVUS_URI', 'your_endpoint'),
        'user': os.getenv('MILVUS_USER', 'user_name'),
        'password': os.getenv('MILVUS_PASSWORD', 'password_goes_here'),
        'secure': True
        },
    'top_k': 10,
    'index_params': {
        'metric_type': 'IP',
        'index_type': 'AUTOINDEX',
        'params': {}
        }
}
```

## ScalarStore (Optional)

The `ScalarStore` is storage of scalar data, which allows information retrieval other than semantic search, such as keyword match. It should follow API design below to adapt operations in chatbot:

**`ScalarStore(index_name: str, client: CLIENT)`**

**Parameters:**

- `index_name (str)`: table name in scalar database
- `client`: method to connect database

**Methods:**

- `insert`: data insert, given a list of documents, returns how many data entities inserted
- `search`: scalar search, given a query in string, returns a list of useful documents

To enable scalar store, you need to set `USE_SCALAR=True` in [config.py](../../config.py).
By default, it uses `ElasticSearch BM25` in LangChain. You can modify [config.py](../../config.py) to configure connection args.

## MemoryStore

The `MemoryStore` records chat history in database. It should follow API design below to adapt operations in chatbot:

**`MemoryStore(table_name: str, session_id: str)`**

**Parameters:**

- `table_name (str)`: table name in database
- `session_id (str)`: identifier for sessions, allowing for different sessions of conversation

**Attributes:**

- `memory (BaseMemory)`: a LangChain base memory to adapt agent

**Methods:**

- `add_history`: insert chat history to database, given a list of dictionaries with keys of 'question' and 'answer', [{'question': 'xxx', 'answer': 'xxx'}]
- `get_history`: return chat history in a list of tuples, [('this is question', 'this is answer')]

By default, it uses `PostgresChatMessageHistory` and `ConversationBufferMemory` in LangChain to build memory. You can modify [`config.py`](../../config.py) to configure it.

