import sys
import argparse
import os
import numpy as np
import pandas as pd
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from akcio.offline_tools.load_to_vector_db import load_to_vector_db
from akcio.offline_tools.generate_questions import get_output_csv
from akcio.embedding import TextEncoder
from tqdm import tqdm


def split_df_by_row(df, n):
    rows_per_df = np.ceil(len(df) / n).astype(int)
    df_list = []
    for i in range(n):
        start = i * rows_per_df
        end = (i + 1) * rows_per_df
        df_list.append(df.iloc[start:end])
    return df_list


def get_named_col_names(df):
    named_col_names = []
    for col_name in df.columns.values.tolist():
        if 'unnamed' not in col_name.lower():
            named_col_names.append(col_name)
    return named_col_names


def get_embedding_array(df, batch_size=64):
    encoder = TextEncoder()
    original_col = get_named_col_names(df)
    print('original_col = ', original_col)
    q_list = []
    embeddings = []
    t1 = time.time()
    for i, question in enumerate(tqdm(df['question'])):
        q_list.append(question)
        if (i + 1) % batch_size == 0 or i == len(df) - 1:
            batch_embeddings = encoder.embed_documents(q_list)
            embeddings.extend(batch_embeddings)
            q_list = []
    t2 = time.time()
    print('time = ', t2 - t1)
    df['question_embedding'] = embeddings
    cols_to_save = original_col + ['question_embedding']

    embeddings_array = df[cols_to_save].to_numpy()
    return embeddings_array


def save_embedding(csv_file, batch_size=64):
    if '|' in os.path.basename(csv_file):
        dst_csv_path = os.path.join(os.path.dirname(csv_file), os.path.basename(csv_file).replace('|', '-'))
        os.rename(csv_file, dst_csv_path)
        csv_file = dst_csv_path
    df = pd.read_csv(csv_file)
    print('len of df =', len(df))

    if 'like' in df.columns:
        df = df.drop(labels='like', axis=1)
    embedding_array = get_embedding_array(df, batch_size=batch_size)
    output_npy_path = f'{csv_file[:-4]}_embedding.npy'
    np.save(output_npy_path, embedding_array)
    print('combined_array.shape = ', embedding_array.shape)
    return output_npy_path


def embed_questions(csv_path, batch_size=64):
    npy_path = f'{csv_path[:-4]}_embedding.npy'
    if os.path.exists(npy_path):
        print('exist...')
        return None
    try:
        npy_path = save_embedding(csv_path, batch_size=batch_size)
        return npy_path
    except Exception as e:
        print('save_embedding failed. ', e)
        return None


def run_loading(project_root_or_file, project_name, mode, url_domain=None, emb_batch_size=64, load_batch_size=256,
                enable_qa=True, qa_num_parallel=8):
    is_root = os.path.exists(project_root_or_file) and os.path.isdir(project_root_or_file)
    if mode != 'custom' and not is_root:
        raise Exception('`project_root_or_file` must be a directory.')
    if mode == 'project':
        if url_domain is None:
            url_domain = os.path.basename(project_root_or_file)
        output_csv = get_output_csv(project_root_or_file, project_name, url_domain, mode=mode, patterns=['*.md'],
                                    enable_qa=enable_qa, num_parallel=qa_num_parallel)

    elif mode == 'github':
        url_domain = 'github.com'
        output_csv = get_output_csv(project_root_or_file, project_name, url_domain, mode=mode,
                                    patterns=['README.*', 'readme.*'], enable_qa=enable_qa, num_parallel=qa_num_parallel)

    # elif mode == 'stackoverflow': #todo
    #     output_csv = stackoverflow_json2csv(project_root_or_file)
    # elif mode == 'custom':  # todo
    #     pass
    #
    # # output_csv: 'file_or_repo', 'question', 'doc_chunk', 'url', 'embedding'
    output_npy = embed_questions(output_csv, batch_size=emb_batch_size)
    print(f'finish embed_questions, output_npy =\n{output_npy}')

    load_to_vector_db(output_npy, project_name, batch_size=load_batch_size, enable_qa=enable_qa)
    print(f'finish load_to_vector_db')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_root_or_file", type=str, required=True,
                        help='It can be a folder or file path containing your project information.')
    parser.add_argument("--project_name", default='', type=str, required=False,
                        help='It is your project name. When mode is `stackoverflow`, project_name is not required.')
    # when mode == 'project',
    # `project_root_or_file` is a repo root which contains **/*.md files.
    # when mode == 'github',
    # `project_root_or_file` can be a repo with '|', or a root containing repo folders with '|'.
    # when mode == 'stackoverflow',
    # `project_root_or_file` can be a project folder containing json files, or a root containing project folders.
    parser.add_argument("--mode", type=str, choices=['project', 'github', 'stackoverflow', 'custom'], required=True,
                        help='''when mode == 'project', `project_root_or_file` is a repo root which contains **/*.md files.
when mode == 'github', `project_root_or_file` can be a repo with '|', or a root containing repo folders with '|'.
when mode == 'stackoverflow', `project_root_or_file` can be a project folder containing json files, or a root containing project folders.''')
    parser.add_argument("--url_domain", type=str, required=False, help='''When the mode is project, you can specify a url domain, so that the relative directory of your file is the same relative path added after your domain.
When the mode is github, there is no need to specify the url, the url path is the url of your github repo.
When the mode is stackoverflow, there is no need to specify the url, because the url can be obtained in the answer json.''')
    parser.add_argument("--emb_batch_size", type=int, required=False, default=64,
                        help='Batch size when extracting embedding.')
    parser.add_argument("--load_batch_size", type=int, required=False, default=256,
                        help='Batch size when loading to vector db.')
    parser.add_argument("--enable_qa", type=bool, required=False, default=True,
                        help='Whether to use the generate question mode, which will use llm to generate questions related to doc chunks, and use questions to match instead of doc chunks.')
    parser.add_argument("--qa_num_parallel", default=8, type=int, required=False)
    # parser.add_argument("--embedding_devices", type=str, default='0,1', required=False)
    args = parser.parse_args()
    t0 = time.time()

    # embedding_devices = [int(device_id) for device_id in args.embedding_devices.split(',')]
    run_loading(args.project_root_or_file, args.project_name, args.mode, args.url_domain, args.emb_batch_size,
                args.load_batch_size, args.enable_qa, args.qa_num_parallel)
    t1 = time.time()
    total_sec = t1 - t0
    print(f'total time = {total_sec} (s) = {total_sec / 3600} (h).')
