from typing import List

from langchain.embeddings.base import Embeddings
from langchain.embeddings import HuggingFaceEmbeddings

from .config import textencoder_config

MODEL = textencoder_config.get('model', 'multi-qa-mpnet-base-cos-v1')
NORM = textencoder_config.get('norm', False)


class TextEncoder(HuggingFaceEmbeddings):
    def __init__(self, *args, **kwargs):
        assert isinstance(self, Embeddings), 'Invalid text encoder. Only accept Langchain embeddings.'
        kwargs['model_name'] = kwargs.get('model_name', MODEL)
        super().__init__(*args, **kwargs)

    def embed_documents(self, texts: List[str], norm: bool = NORM) -> List[List[float]]:
        embeds = super().embed_documents(texts)
        if norm:
            import numpy
            embeds = [(x / numpy.linalg.norm(x)).tolist() for x in embeds]
        return embeds
    
    def embed_query(self, text: str, norm: bool = NORM) -> List[float]:
        embed = super().embed_query(text)
        if norm:
            import numpy
            embed /= numpy.linalg.norm(embed)
            embed = embed.tolist()
        return embed