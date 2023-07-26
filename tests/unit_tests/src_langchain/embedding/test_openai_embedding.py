import os
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))
from src_langchain.embedding.openai_embedding import TextEncoder


class TestOpenAIEmbedding(unittest.TestCase):
    np.random.seed(42)
    rand_emb = np.random.rand(64, )

    def test_embed_query(self):
        with patch('langchain.embeddings.OpenAIEmbeddings.embed_query') as mock_embed:
            mock_embed.return_value = self.rand_emb
            text_encoder = TextEncoder(openai_api_key='mock-key')
            res = text_encoder.embed_query('mock query')
            self.assertEqual(self.rand_emb.tolist(), res)

    def test_embed_documents(self):
        with patch('langchain.embeddings.OpenAIEmbeddings.embed_documents') as mock_embed:
            mock_embed.return_value = [self.rand_emb.tolist()]
            text_encoder = TextEncoder(openai_api_key='mock-key')
            res = text_encoder.embed_documents(['mock query'], norm=False)
            self.assertEqual([self.rand_emb.tolist()], res)


if __name__ == '__main__':
    unittest.main()
