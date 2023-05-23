# Data Loader

The `DataLoader` parses documents from given data source and split documents into a list of doc chunks.

By default, it allows files or urls as data source, and uses Langchain `RecursiveCharacterTextSplitter` to split documents.

To configure it, you can modify [config.py](./config.py) to change parameters like chunk size.

## APIs

**`DataLoader(splitter)`:**

- `splitter (TextSplitter)`: a Langchain text splitter, defaults to RecursiveCharacterTextSplitter with chunk size in config.py

### Methods

**`__call__(data_src, source_type='file')`:**

- `data_src`: (a list of) file path, file-like object, or url
- `source_type (str)`: type of data source, either 'file' or 'url'.

### Example Usage

```python
from data_loader import DataLoader

load_data = DataLoader()

# Or use your splitter
# load_data = DataLoader(splitter=MySplitter(chunk_size=100))

docs = load_data(data_src='path/to/doc')

# Or load from urls
# docs = load_data(data_src='https://zilliz.com/doc/about_zilliz_cloud', source_type='url')
```

## Customize DataLoader

Modify `DataLoader` in [__init__.py](./__init__.py).

```python
from langchain.text_splitter import TextSplitter

from .data_splitter import MarkDownSplitter
from .config import dataloader_config


CHUNK_SIZE = dataloader_config.get('chunk_size', 300)

class DataLoader:
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