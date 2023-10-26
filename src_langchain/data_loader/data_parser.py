from config import DATAPARSER_CONFIG  # pylint: disable=C0413
import os
import sys

from typing import List, Optional
import tiktoken
from langchain.docstore.document import Document
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


CHUNK_SIZE = DATAPARSER_CONFIG.get('chunk_size', 300)


class DataParser:
    '''Load data from urls or files (paths or file-like objects) as a list of doc chunks'''

    def __init__(self,
                 splitter: TextSplitter = RecursiveCharacterTextSplitter(
                     chunk_size=CHUNK_SIZE),
                 token_model: str = 'gpt-3.5-turbo'
                 ):
        self.splitter = splitter
        self.enc = tiktoken.encoding_for_model(token_model)

    def __call__(self, data_src, source_type: str = 'file') -> List[str]:
        if not isinstance(data_src, list):
            data_src = [data_src]
        if source_type == 'file':
            docs = self.from_files(data_src)
        elif source_type == 'url':
            docs = self.from_urls(data_src)
        else:
            raise AttributeError(
                'Invalid source type. Only support "file" or "url".')

        docs = self.splitter.split_documents(docs)
        docs = [str(doc.page_content) for doc in docs]
        token_count = 0
        for doc in docs:
            token_count += len(self.enc.encode(doc))
        return docs, token_count

    def from_files(self, files: list, encoding: Optional[str] = 'utf-8') -> List[Document]:
        '''Load documents from path or file-like object, return a list of unsplit LangChain Documents'''
        docs = []
        for file in files:
            if hasattr(file, 'name'):
                file_path = file.name
            else:
                file_path = file
            with open(file_path, encoding=encoding) as f:
                text = f.read()
            metadata = {'source': file_path}
            docs.append(Document(page_content=text, metadata=metadata))
        return docs

    def from_urls(self, urls: List[str]) -> List[Document]:
        from langchain.document_loaders import UnstructuredURLLoader  # pylint: disable=C0415

        loader = UnstructuredURLLoader(urls=urls)
        docs = loader.load()
        return docs
