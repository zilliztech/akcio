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

By default, it uses `Milvus` in Langchain. You can modify `config.py` to configure it.

## ScalarStore

The `ScalarStore` is storage of scalar data, which allows information retrieval other than semantic search, such as keyword match. It should follow API design below to adapt operations in chatbot:

**`ScalarStore(index_name: str, client: CLIENT)`**

**Parameters:**

- `index_name (str)`: table name in scalar database
- `client`: method to connect database

**Methods:**

- `insert`: data insert, given a list of documents, returns how many data entities inserted
- `search`: scalar search, given a query in string, returns a list of useful documents

By default, it uses `ElasticSearch BM25` in Langchain. You can modify `config.py` to configure connection args.

## MemoryStore

The `MemoryStore` records chat history in database. It should follow API design below to adapt operations in chatbot:

**`MemoryStore(table_name: str, session_id: str)`**

**Parameters:**

- `table_name (str)`: table name in database
- `session_id (str)`: identifier for sessions, allowing for different sessions of conversation

**Attributes:**

- `memory (BaseMemory)`: a Langchain base memory to adapt agent

**Methods:**

- `add_history`: insert chat history to database, given a list of dictionaries with keys of 'question' and 'answer', [{'question': 'xxx', 'answer': 'xxx'}]
- `get_history`: return chat history in a list of tuples, [('this is question', 'this is answer')]

By default, it uses `PostgresChatMessageHistory` and `ConversationBufferMemory` in Langchain to build memory. You can modify `config.py` to configure it.

