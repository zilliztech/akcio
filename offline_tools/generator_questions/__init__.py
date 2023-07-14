import sys
import pandas as pd
import csv
import multiprocessing
import os
from datetime import datetime
from glob import glob
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from offline_tools.generator_questions.question_generator import QuestionGenerator  # pylint: disable=C0413


def get_named_col_names(df):
    named_col_names = []
    for col_name in df.columns.values.tolist():
        if 'unnamed' not in col_name.lower():
            named_col_names.append(col_name)
    return named_col_names


def get_file_or_repo(data_dir, f, mode):
    if mode == 'project':
        file_or_repo = os.path.relpath(f, data_dir)
    else:
        if '|' in os.path.basename(data_dir):  # when data_dir is a repo with '|'
            file_or_repo = os.path.basename(data_dir).replace('|', '/')
        else:  # when data_dir is a root containing repo folders with '|'
            replaced_rel_path = os.path.relpath(f, data_dir).replace('|', '/')
            file_or_repo = replaced_rel_path[:replaced_rel_path.rfind('/')]
    return file_or_repo


def run_batch(arg: dict):
    files = arg['files']
    data_dir = arg['data_dir']
    existed_files = arg['existed_files']
    mode = arg['mode']
    project_name = arg['project_name']
    chat_cli = arg['chat_cli']
    target_csv = arg['target_csv']
    header = arg['header']
    FILE_OR_REPO = arg['FILE_OR_REPO']  # pylint: disable=C0103
    for f in files:
        if os.path.isfile(f):
            if os.path.relpath(f, data_dir) in existed_files:
                print('f in existed_files, continue...')
                continue

            try:
                print(f'Start for {f}...')
                with open(f, 'r', encoding='utf-8') as doc_f:
                    doc = doc_f.read()
                if mode == 'github' and (project_name is None or project_name == ''):
                    project = os.path.basename(os.path.dirname(f)).split('/')[-1].split('|')[-1]
                    print('project = ', project)  # todo
                else:
                    project = project_name
                questions = chat_cli.generate_qa(doc=doc, project=project)
                assert len(questions) > 0, 'No questions.'
                print('Writing questions to csv ...')
                with open(target_csv, 'a+', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=header)
                    for q in questions:
                        if q is None:
                            raise ValueError('Failed for Invalid question value (None).')
                        else:
                            file_or_repo = get_file_or_repo(data_dir, f, mode)
                            writer.writerow({
                                FILE_OR_REPO: file_or_repo,
                                'question': q[0],
                                'doc_chunk': q[1]
                            })
                print(f'Done for {f}\n')
            except Exception as e:  # pylint: disable=W0703
                print(f'Failed for {f}:\n {e}\n')
        else:
            print(f'Invalid file: {f}\n')


def try_generate_questions(data_dir, project_name, mode, patterns, num_parallel=8, existed_files=set()):  # pylint: disable=W0102
    chat_cli = QuestionGenerator()

    src_pattern_files = []
    for pattern in patterns:
        src_pattern_files.extend(glob(os.path.join(data_dir, '**', pattern), recursive=True))

    pattern_files = []
    for pattern_file in src_pattern_files:
        if not os.path.relpath(pattern_file, data_dir) in existed_files:
            pattern_files.append(pattern_file)

    target_csv = data_dir + '.csv'

    FILE_OR_REPO = 'file' if mode == 'project' else 'repo'  # pylint: disable=C0103

    header = [FILE_OR_REPO, 'question', 'doc_chunk']
    if not os.path.exists(target_csv):
        with open(target_csv, 'a+', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()

    now = datetime.now()
    print(now.strftime('%Y-%m-%d %H:%M:%S'))

    batches = []
    max_batch_size = len(pattern_files) // num_parallel + 1
    for i in range(0, len(pattern_files), max_batch_size):
        batches.append(pattern_files[i: i + max_batch_size])
    assert len(batches) <= num_parallel, 'Invalid batch nums'
    args = []
    for batch_files in batches:
        args.append({'files': batch_files,
                     'data_dir': data_dir,
                     'existed_files': existed_files,
                     'mode': mode,
                     'project_name': project_name,
                     'chat_cli': chat_cli,
                     'target_csv': target_csv,
                     'header': header,
                     'FILE_OR_REPO': FILE_OR_REPO})
    with multiprocessing.Pool(num_parallel) as pool:
        pool.map(run_batch, args)
    finished_files = existed_files
    if os.path.exists(target_csv):
        finished_df = pd.read_csv(target_csv)
        finished_files.update(set(finished_df[FILE_OR_REPO]))
    print(f'Finish one try, len of finished_files = {len(finished_files)}')
    return finished_files


def get_output_csv(data_dir, project_name, domain, mode, patterns, enable_qa=True, num_parallel=8):
    if mode == 'github':
        FILE_OR_REPO = 'repo'  # pylint: disable=C0103
    else:
        FILE_OR_REPO = 'file'  # pylint: disable=C0103

    pattern_files = []
    for pattern in patterns:
        pattern_files.extend(glob(os.path.join(data_dir, '**', pattern), recursive=True))
    print(f'len of pattern_files = {len(pattern_files)}')

    total_lines = 0
    for file in tqdm(pattern_files):
        with open(file, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
            total_lines += lines
    print('Total number of lines in pattern_files:', total_lines)

    csv_file = data_dir + '.csv'

    if enable_qa:
        finished_files = set()
        if os.path.exists(csv_file):
            exist_df = pd.read_csv(csv_file)

            finished_files = set(exist_df[FILE_OR_REPO].value_counts().index.to_list())
            print('finished_files num = ', len(finished_files))

        for _ in range(2):
            finished_files = try_generate_questions(data_dir, project_name, mode, patterns, num_parallel,
                                                    existed_files=finished_files)

    else:
        chat_cli = QuestionGenerator()
        pattern_files = []
        for pattern in patterns:
            pattern_files.extend(glob(os.path.join(data_dir, '**', pattern), recursive=True))

        header = [FILE_OR_REPO, 'doc_chunk']
        if not os.path.exists(csv_file):
            with open(csv_file, 'a+', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()

        for f in pattern_files:
            if os.path.isfile(f):
                with open(f, 'r', encoding='utf-8') as doc_f:
                    doc = doc_f.read()
                doc_chunk_list = chat_cli.split_doc(doc=doc)

                with open(csv_file, 'a+', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=header)
                    for doc_chunk in doc_chunk_list:
                        file_or_repo = get_file_or_repo(data_dir, f, mode)
                        writer.writerow({
                            FILE_OR_REPO: file_or_repo,
                            'doc_chunk': doc_chunk
                        })

    df = pd.read_csv(csv_file)
    if domain[-1] == '/':
        domain = domain[:-1]


    def add_url_column(df, domain):
        if 'url' not in df.columns:
            df['url'] = ''

        for i in tqdm(range(len(df))):
            file_path = df.loc[i, FILE_OR_REPO]
            if mode != 'github':
                file_path = os.path.join(*os.path.split(file_path)[:-1])
            url = domain + '/' + file_path
            df.loc[i, 'url'] = url

        print(f'final len of df = {len(df)}')
        df.to_csv(csv_file, index=False)  # overwrite

    add_url_column(df, domain)
    return csv_file
