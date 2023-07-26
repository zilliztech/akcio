from typing import List
import sys
import os

from langchain.embeddings.base import Embeddings
from langchain.embeddings import OpenAIEmbeddings

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import TEXTENCODER_CONFIG # pylint: disable=C0413


MODEL = TEXTENCODER_CONFIG.get('model', 'text-embedding-ada-002')
NORM = TEXTENCODER_CONFIG.get('norm', False)


class TextEncoder(OpenAIEmbeddings):
    '''Text encoder converts text input(s) into embedding(s)'''
    def __init__(self, *args, **kwargs):
        assert isinstance(
            self, Embeddings), 'Invalid text encoder. Only accept LangChain embeddings.'
        kwargs['model'] = kwargs.get('model_name', MODEL)
        super().__init__(*args, **kwargs)

    def embed_documents(self, texts: List[str], norm: bool = NORM, chunk_size: int = 1000) -> List[List[float]]:
        embeds = super().embed_documents(texts, chunk_size=chunk_size)
        if norm:
            import numpy  # pylint: disable=C0415
            embeds = [(x / numpy.linalg.norm(x)).tolist() for x in embeds]
        return embeds

    def embed_query(self, text: str, norm: bool = NORM) -> List[float]:
        embed = super().embed_query(text)
        if norm:
            import numpy  # pylint: disable=C0415
            embed /= numpy.linalg.norm(embed)
            embed = embed.tolist()
        return embed
