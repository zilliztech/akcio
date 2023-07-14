import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))

from src_langchain.data_loader import DataParser


class TestDataParser(unittest.TestCase):
    data_parser = DataParser(
        splitter=RecursiveCharacterTextSplitter(chunk_size=2, chunk_overlap=0, length_function=len))

    def test_call_from_files(self):
        with tempfile.NamedTemporaryFile(suffix='.txt') as fp:
            text = 'ab\ncd'
            tmp_file_path = fp.name
            with io.open(tmp_file_path, 'w') as file:
                file.write(text)
            output = self.data_parser(tmp_file_path, source_type='file')
            assert output == ['ab', 'cd']

    def test_call_from_urls(self):
        with patch('langchain.document_loaders.UnstructuredURLLoader.load') as mock_url_loader:
            mock_url_loader.return_value = [Document(page_content='ab\ncd', metadata={})]
            output = self.data_parser('www.mockurl.com', source_type='url')
            assert output == ['ab', 'cd']


if __name__ == '__main__':
    unittest.main()
