import io
import tempfile
import unittest
from unittest.mock import patch

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


from src.langchain.data_loader import DataParser


class TestDataParser(unittest.TestCase):
    data_parser = DataParser(
        splitter=RecursiveCharacterTextSplitter(chunk_size=2, chunk_overlap=0, length_function=len))

    def test_call_from_files(self):
        with tempfile.NamedTemporaryFile(suffix='.txt') as fp:
            text = 'ab\ncd'
            tmp_file_path = fp.name
            with io.open(tmp_file_path, 'w') as file:
                file.write(text)
            output, token_count = self.data_parser(tmp_file_path, source_type='file')
            assert output == ['ab', 'c', 'd'], token_count == 3

    def test_call_from_urls(self):
        with patch('langchain.document_loaders.UnstructuredURLLoader.load') as mock_url_loader:
            mock_url_loader.return_value = [Document(page_content='ab\ncd', metadata={})]
            output, token_count = self.data_parser('www.mockurl.com', source_type='url')
            assert output == ['ab', 'c', 'd'], token_count == 3


if __name__ == '__main__':
    unittest.main()
