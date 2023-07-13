import os
import json
import pandas as pd

from glob import glob
from tqdm import tqdm

max_len = 350 - 65


def count_token(doc):
    doc_len = len(doc) // 3
    return doc_len


def get_best_answer(answers):
    # if len(answers) > 1:
    too_long = False
    best_answer = answers[0]
    for answer in answers:
        if answer['best_answer']:
            best_answer = answer
            break
    best_answer_body = best_answer['body']
    now_len = count_token(best_answer_body)
    if now_len > max_len:
        too_long = True
    # while now_len > max_len:
    #     now_answer_body = SummarizeHelper(summarize_type='transformers').transformer_safe_summarize(best_answer_body)
    #     print(f'summary...\n before: \n {best_answer_body}\n after: \n{now_answer_body}')
    #     now_len = count_token(now_answer_body)
    #     best_answer_body = now_answer_body
    return best_answer_body, too_long


def json_to_csv(json_root, dst_csv_path):
    too_long_q_num = 0
    not_too_long_q_num = 0
    good_df_row_list = []
    bad_df_row_list = []
    for json_file in glob(os.path.join(json_root, '*.json')):
        with open(json_file, 'r') as f:
            data = json.load(f)
            for question_dict in tqdm(data['questions']):
                if 'title' not in question_dict or question_dict['title'] == '':
                    continue
                title = question_dict['title']
                answers = question_dict['answers']
                url = question_dict['url']
                best_answer_body, too_long = get_best_answer(answers)

                question_body = question_dict['question']['body']
                # print(f'question:\n{question_body}\n========')
                answer_with_question = question_body + '\n' + best_answer_body
                if count_token(answer_with_question) <= max_len:
                    doc_chunk = answer_with_question
                else:
                    doc_chunk = best_answer_body
                relative_json_path = os.path.relpath(json_file, os.path.dirname(
                    json_root))  # os.path.join(*json_file.split('/')[3:])
                if too_long:
                    too_long_q_num += 1
                    bad_df_row_list.append(
                        {'question': title, 'doc_chunk': doc_chunk, 'file': relative_json_path, 'url': url})
                else:
                    not_too_long_q_num += 1
                    good_df_row_list.append(
                        {'question': title, 'doc_chunk': doc_chunk, 'file': relative_json_path, 'url': url})

    good_df = pd.DataFrame(good_df_row_list)
    bad_df = pd.DataFrame(bad_df_row_list)
    order = ['file', 'question', 'doc_chunk', 'url']
    if len(good_df) > 0:
        good_df = good_df[order]
    if len(bad_df) > 0:
        bad_df = bad_df[order]
    # print(good_df)

    bad_path = os.path.splitext(dst_csv_path)[0] + '_toolong' + os.path.splitext(dst_csv_path)[1]
    # print('dst_csv_path = ', dst_csv_path)
    # print('bad_path = ', bad_path)
    good_df.to_csv(dst_csv_path, index=False)
    if len(bad_df) > 0:
        bad_df.to_csv(bad_path, index=False)
    # print('too_long_q_num = ', too_long_q_num)
    # print('not_too_long_q_num = ', not_too_long_q_num)
    return dst_csv_path, bad_path


def concat_csv(dst_csv_path_list, root_or_folder):
    df_list = []
    for file_path in dst_csv_path_list:
        try:  # empty file
            df = pd.read_csv(file_path)
            df_list.append(df)
        except:
            continue
        os.remove(file_path)
    merged_df = pd.concat(df_list)
    merged_csv_path = root_or_folder + '.csv'
    merged_df.to_csv(merged_csv_path, index=False)
    return merged_csv_path


def stackoverflow_json2csv(root_or_folder):
    is_project_folder = False
    for file in os.listdir(root_or_folder):
        if file.endswith('.json'):
            is_project_folder = True
            break
    if not is_project_folder:
        dst_csv_path_list = []
        bad_path_list = []
        for mid_folder in os.listdir(root_or_folder):
            mid_path = os.path.join(root_or_folder, mid_folder)
            if os.path.isdir(mid_path):
                output_csv = mid_path + '.csv'
                dst_csv_path, bad_path = json_to_csv(mid_path, output_csv)
                dst_csv_path_list.append(dst_csv_path)
                bad_path_list.append(bad_path)
        merged_csv_path = concat_csv(dst_csv_path_list, root_or_folder)
        _ = concat_csv(bad_path_list, root_or_folder + '_too_long')
        return merged_csv_path
    else:
        output_csv = root_or_folder + '.csv'
        dst_csv_path, _ = json_to_csv(root_or_folder, output_csv)
        return dst_csv_path
