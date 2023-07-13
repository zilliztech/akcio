import os
import sys

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_src.store import DocStore


class DBReader(object):
    def __init__(self, path):
        self.path = path
        self.db = np.load(path, allow_pickle=True)[()]

    def __len__(self):
        return len(self.db)

    def __iter__(self):
        for row in self.db:
            yield row


def langchain_load(npy_path, project, batch_size=128, enable_qa=True):
    if enable_qa:
        # file, question, doc_chunk, url, embedding
        doc_chunk_col_ind = 2
        embedding_col_ind = 4
        question_col_ind = 1
    else:
        # file, doc_chunk, url, embedding
        doc_chunk_col_ind = 1
        embedding_col_ind = 3
    reader = DBReader(npy_path)
    doc_db = DocStore(table_name=project, use_scalar=True)
    row_ind = 0
    it = iter(reader)
    batch_rows = []
    while True:
        # print(row_ind)
        try:
            row = next(it)
            # print(row)
            batch_rows.append(row)
            if (row_ind + 1) % batch_size == 0 or row_ind == len(reader) - 1:
                data = [row[embedding_col_ind] for row in batch_rows]
                if enable_qa:
                    metadatas = [{'text': row[question_col_ind], 'doc': row[doc_chunk_col_ind]} for row in batch_rows]
                else:
                    metadatas = [{'text': row[doc_chunk_col_ind]} for row in batch_rows]
                doc_db.insert_embeddings(data, metadatas)
                batch_rows = []
        except StopIteration:
            break
        row_ind += 1
    # print('row_ind = ', row_ind)


if __name__ == '__main__':
    langchain_load(npy_path='you npy file path', project='your project name')
