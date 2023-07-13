# Data Parser

The `DataParser` parses documents from given data source and split documents into a list of doc chunks.

By default, it allows files or urls as data source, and uses LangChain `RecursiveCharacterTextSplitter` to split documents.

To configure it, you can modify [config.py](../../config.py) to change parameters like chunk size.

## APIs

**`DataParser(splitter)`:**

- `splitter (TextSplitter)`: a LangChain text splitter, defaults to RecursiveCharacterTextSplitter with chunk size in config.py

### Methods

**`__call__(data_src, source_type='file')`:**

- `data_src`: (a list of) file path, file-like object, or url
- `source_type (str)`: type of data source, either 'file' or 'url'.

### Example Usage

```python
from data_parser import DataParser

load_data = DataParser()

# Or use your splitter
# load_data = DataParser(splitter=MySplitter(chunk_size=100))

docs = load_data(data_src='path/to/doc')

# Or load from urls
# docs = load_data(data_src='https://zilliz.com/doc/about_zilliz_cloud', source_type='url')
```

## Customize DataParser

Modify `DataParser` in [data_parser.py](./data_parser.py).

```python
import os
import sys
from langchain.text_splitter import TextSplitter
from .data_splitter import MarkDownSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from config import dataparser_configs


CHUNK_SIZE = dataparser_config.get('chunk_size', 300)

class DataParser:
    def __init__(self,
                 splitter: TextSplitter = MarkDownSplitter(chunk_size=CHUNK_SIZE),
                 ):
        self.splitter = splitter

    def __call__(self, data_src, source_type: str = 'file') -> List[str]:
      if source_type == 'file':
        with open(f, 'r') as f:
          content = f.read()

      docs = customized_method(content)
      doc_chunks = self.splitter(docs)
      return doc_chunks
```

### Load via third-party loaders

If you want to use third-party loaders, you can add your `source_type`, and define your custom load function.

#### Using LangChain Loader
   
For example, if you want to load arxiv, you can use [LangChain Arxiv Loader](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/arxiv.html).
```python
import os
import sys
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from config import dataparser_configs


CHUNK_SIZE = dataparser_config.get('chunk_size', 300)

class DataParser:
    '''Load data from urls or files (paths or file-like objects) as a list of doc chunks'''
    def __init__(self,
                 splitter: TextSplitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE)
                 ):
        self.splitter = splitter

    def __call__(self, data_src, source_type: str = 'file') -> List[str]:
        if not isinstance(data_src, list):
            data_src = [data_src]
        if source_type == 'arxiv':
            docs = self.from_arxiv(data_src)
        else:
            raise AttributeError('Invalid source type. Only support "file" or "url".')

        docs = self.splitter.split_documents(docs)
        return [str(doc.page_content) for doc in docs]
    
    def from_arxiv(self, data_src, **kwargs):
        from langchain.document_loaders import ArxivLoader
        docs = ArxivLoader(query=data_src, **kwargs).load()
        return docs

```

#### Using LlammaIndex Reader  

For example, if you want to load from discord, you can use [LlammaIndex Discord Reader](https://gpt-index.readthedocs.io/en/latest/examples/data_connectors/DiscordDemo.html).

```python
import os
import sys
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from config import dataparser_configs


CHUNK_SIZE = dataparser_config.get('chunk_size', 300)

class DataParser:
    '''Load data from urls or files (paths or file-like objects) as a list of doc chunks'''
    def __init__(self,
                 splitter: TextSplitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE)
                 ):
        self.splitter = splitter

    def __call__(self, data_src, source_type: str = 'file') -> List[str]:
        if not isinstance(data_src, list):
            data_src = [data_src]
        if source_type == 'arxiv':
            docs = self.from_discord(data_src)
        else:
            raise AttributeError('Invalid source type. Only support "file" or "url".')

        docs = self.splitter.split_documents(docs)
        return [str(doc.page_content) for doc in docs]
    
    def from_discord(self, channel_ids):
        from llama_index import DiscordReader
        discord_token = "YOUR_DISCORD_TOKEN"
        channel_ids = [channel_ids]
        docs = DiscordReader(discord_token=discord_token).load_data(channel_ids=channel_ids)
        return docs
```