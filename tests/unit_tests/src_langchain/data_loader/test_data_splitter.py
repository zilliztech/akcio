import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from src_langchain.data_loader.data_splitter import MarkDownSplitter


class TestMarkDownSplitter(unittest.TestCase):
    data_splitter = MarkDownSplitter(chunk_size=6, chunk_overlap=0)

    def test_split_text(self):
        text = '# Title\nABC\n## Subtitle1\nabc1\n## Subtitle2\nabc2'
        output = self.data_splitter.split_text(text)
        assert output == ['# Title\nABC', '# Title\n## Subtitle1\nabc1', '# Title\n## Subtitle2\nabc2']


if __name__ == '__main__':
    unittest.main()
