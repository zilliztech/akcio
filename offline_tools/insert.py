import sys
import os
from tqdm import tqdm
import numpy as np
import pandas as pd
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.langchain.embedding import TextEncoder  # pylint: disable=C0413
from offline_tools.generator_questions import get_output_csv  # pylint: disable=C0413
from offline_tools.utils.stackoverflow_json2csv import stackoverflow_json2csv  # pylint: disable=C0413
from offline_tools.utils.load_npy import langchain_load  # pylint: disable=C0413


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


def get_embedding_array(df, enable_qa=True, batch_size=64):
    encoder = TextEncoder()
    original_col = get_named_col_names(df)
    print('original_col = ', original_col)
    q_list = []
    embeddings = []
    t1 = time.time()
    if enable_qa:
        emb_col = 'question'
    else:
        emb_col = 'doc_chunk'
    for i, question in enumerate(tqdm(df[emb_col])):
        q_list.append(question)
        if (i + 1) % batch_size == 0 or i == len(df) - 1:
            batch_embeddings = encoder.embed_documents(q_list)
            embeddings.extend(batch_embeddings)
            q_list = []
    t2 = time.time()
    print('time = ', t2 - t1)
    df['embedding'] = embeddings
    cols_to_save = original_col + ['embedding']

    embeddings_array = df[cols_to_save].to_numpy()
    return embeddings_array


def save_embedding(csv_file, enable_qa=True, batch_size=64):
    if '|' in os.path.basename(csv_file):
        dst_csv_path = os.path.join(os.path.dirname(
            csv_file), os.path.basename(csv_file).replace('|', '-'))
        os.rename(csv_file, dst_csv_path)
        csv_file = dst_csv_path
    df = pd.read_csv(csv_file)
    print('len of df =', len(df))

    if 'like' in df.columns:
        df = df.drop(labels='like', axis=1)
    embedding_array = get_embedding_array(
        df, enable_qa=enable_qa, batch_size=batch_size)
    output_npy_path = f'{csv_file[:-4]}_embedding.npy'
    np.save(output_npy_path, embedding_array)
    print('combined_array.shape = ', embedding_array.shape)
    return output_npy_path


def embed_questions(csv_path, enable_qa=True, batch_size=64):
    npy_path = f'{csv_path[:-4]}_embedding.npy'
    if os.path.exists(npy_path):
        print('exist...')
        return npy_path
    try:
        npy_path = save_embedding(
            csv_path, enable_qa=enable_qa, batch_size=batch_size)
        return npy_path
    except Exception as e:  # pylint: disable=W0703
        print('save_embedding failed. ', e)
        return None


def run_loading(project_root_or_file, project_name, mode, url_domain=None, emb_batch_size=64, load_batch_size=256,
                enable_qa=True, qa_num_parallel=8, platform='towhee'):
    is_root = os.path.exists(
        project_root_or_file) and os.path.isdir(project_root_or_file)
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

    elif mode == 'stackoverflow':
        output_csv = stackoverflow_json2csv(project_root_or_file)
    # elif mode == 'custom':  # todo
    #     pass
    #
    # # output_csv: 'file_or_repo', 'question', 'doc_chunk', 'url', 'embedding'
    output_npy = embed_questions(
        output_csv, enable_qa=enable_qa, batch_size=emb_batch_size)
    print(f'finish embed_questions, output_npy =\n{output_npy}')

    if platform == 'langchain':
        langchain_load(output_npy, project_name,
                       batch_size=load_batch_size, enable_qa=enable_qa)
    elif platform == 'towhee':
        raise ValueError(
            'The offline tool for Towhee option is not supported yet.')
    print('finish load_to_vector_db')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', type=str, default='towhee', choices=['towhee', 'langchain'],
                        help='It is your option of platform to build the system.')
    parser.add_argument('--project_root_or_file', type=str, required=True,
                        help='It can be a folder or file path containing your project information.')
    parser.add_argument('--project_name', type=str, required=True,
                        help='It is your project name. It is also the collection_name in the vector database.')
    # when mode == 'project',
    # `project_root_or_file` is a repo root which contains **/*.md files.
    # when mode == 'github',
    # `project_root_or_file` can be a repo with '|', or a root containing repo folders with '|'.
    # when mode == 'stackoverflow',
    # `project_root_or_file` can be a project folder containing json files, or a root containing project folders.
    parser.add_argument('--mode', type=str, choices=['project', 'github', 'stackoverflow', 'custom'], required=True,
                        help='''When mode == 'project', `project_root_or_file` is a repo root which contains **/*.md files.
When mode == 'github', `project_root_or_file` can be a repo with '|', which means "(namespace)|(repo_name)", or a root containing repo folders with '|'.
When mode == 'stackoverflow', `project_root_or_file` can be a project folder containing json files, or a root containing project folders.''')
    parser.add_argument('--url_domain', type=str, required=False,
                        help='''When the mode is project, you can specify a url domain, \
                        so that the relative directory of your file is the same relative path added after your domain.
When the mode is github, there is no need to specify the url, the url path is the url of your github repo.
When the mode is stackoverflow, there is no need to specify the url, because the url can be obtained in the answer json.''')
    parser.add_argument('--emb_batch_size', type=int, required=False, default=64,
                        help='Batch size when extracting embedding.')
    parser.add_argument('--load_batch_size', type=int, required=False, default=256,
                        help='Batch size when loading to vector db.')
    parser.add_argument('--enable_qa', type=int, required=False, default=1,
                        help='Whether to use the generate question mode, which will use llm to generate questions related to doc chunks, \
                            and use questions to match instead of doc chunks. When the mode is stackoverflow, no need to specify it.')
    parser.add_argument('--qa_num_parallel', default=8, type=int, required=False,
                        help='The number of concurrent request when generating problems. \
                            If your openai account does not support high request rates, I suggest you set this value very small, such as 1, \
                                else you can use a higher num such as 8, or 16. When the mode is stackoverflow, no need to specify it.')
    # parser.add_argument("--embedding_devices", type=str, default='0,1', required=False)
    args = parser.parse_args()

    test_enable_qa = bool(args.enable_qa == 0)
    t0 = time.time()
    if args.project_root_or_file.endswith('/'):
        args.project_root_or_file = args.project_root_or_file[:-1]
    # embedding_devices = [int(device_id) for device_id in args.embedding_devices.split(',')]
    run_loading(args.project_root_or_file, args.project_name, args.mode, args.url_domain, args.emb_batch_size,
                args.load_batch_size, test_enable_qa, args.qa_num_parallel, args.platform)
    test_t1 = time.time()
    total_sec = test_t1 - t0
    print(f'total time = {total_sec} (s) = {total_sec / 3600} (h).')
