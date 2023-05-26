import os
import re
from typing import Optional, List
from langchain.chat_models.base import BaseChatModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

from llm.config import chatai_configs
from langchain.schema import (
    SystemMessage
)
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI


class QuestionGenerator:
    '''Use LLM to generate potential questions given document.'''
    temperature: float = chatai_configs.get('temperature', 0.0)
    openai_api_key: Optional[str] = chatai_configs.get('openai_api_key', os.getenv('OPENAI_API_KEY'))
    max_tokens: Optional[int] = chatai_configs.get('max_tokens', None)

    chat: BaseChatModel = ChatOpenAI(temperature=temperature, openai_api_key=openai_api_key)

    def generate_qa(self, doc: str, project: str, chunk_size: int = 300):
        no_answer_str = 'NO ANSWER'
        question_list_str = 'question_list'
        answer_list_str = 'answer_list'

        docs = self.split_doc(doc, chunk_size)
        all_q_doc_list = []
        for doc_chunk in tqdm(docs):
            human_template = '''The first step is to generate some meaningful questions according to the following doc chunk.
In the second step, according to the content of the doc chunk, answer the answer to each question in the first step. Note if the corresponding answer cannot be found in the doc chunk, the answer is a str: "{no_answer_str}".

{format_instructions}
====================================================
Doc chunk of an open-source project {project}:
----------------------------------------------------
{doc}
----------------------------------------------------
'''

            response_schemas = [
                ResponseSchema(name=question_list_str,
                               description="List[str] of questions generated in the first step."),
                ResponseSchema(name=answer_list_str,
                               description=f'''List[str] of answers for the second step, corresponding to the questions generated in the first step. If the corresponding answer cannot be found in the doc chunk, the answer is a str: "{no_answer_str}".''')
            ]
            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
            format_instructions = output_parser.get_format_instructions()

            prompt = ChatPromptTemplate(
                messages=[
                    SystemMessage(
                        content="You are a powerful assistant that can help generate QA on any project documentation."),
                    HumanMessagePromptTemplate.from_template(human_template)
                ],
                input_variables=["project", "doc", "no_answer_str"],
                partial_variables={"format_instructions": format_instructions}
            )
            _input = prompt.format_prompt(project=project, doc=doc_chunk, no_answer_str=no_answer_str)
            output = self.chat(_input.to_messages())
            output_dict = output_parser.parse(output.content)
            try:
                questions = self.get_questions_from_dict(output_dict, no_answer_str, question_list_str, answer_list_str)
                all_q_doc_list.extend([(question, doc_chunk) for question in questions])
            except:
                print('Warn! parse_output_dict() failed.')
                continue
        return all_q_doc_list

    def get_questions_from_dict(self, output_dict, no_answer_str, question_list_str, answer_list_str):
        question_list = output_dict[question_list_str]
        answer_list = output_dict[answer_list_str]
        good_questions = []
        assert len(question_list) == len(answer_list)
        for question, answer in zip(question_list, answer_list):
            if answer != no_answer_str:
                good_questions.append(question)
        return good_questions

    def split_doc(self, doc: str, max_len: int) -> List[str]:
        if self.count_token(doc) < max_len:
            docs = [doc]
        else:
            lines = doc.split('\n')
            new_lines = self.remove_long_code(lines, max_len)
            docs = []
            markdown_splitter = RecursiveCharacterTextSplitter(chunk_size=max_len, chunk_overlap=0,
                                                               length_function=lambda x: self.count_token(
                                                                   x))  # , chunk_overlap=100)
            documents = markdown_splitter.create_documents(['\n'.join(new_lines)])
            # for doc_chunk in documents:
            #     print(doc_chunk.page_content)
            #     print('-' * 100)

            # Keep parent title
            now_title_stack = []
            for doc_chunk in documents:
                new_chunk = []
                lines = doc_chunk.page_content.split('\n')
                for inner_idx, line in enumerate(lines):
                    if line.strip() == '':
                        continue
                    if self.is_title(line):
                        now_head_level = self.get_level(line)
                        last_level_in_stack = self.get_last_level(now_title_stack)
                        while now_head_level <= last_level_in_stack:
                            now_title_stack.pop()
                            last_level_in_stack = self.get_last_level(now_title_stack)
                        now_title_stack.append(line)
                    if inner_idx == 0 and line.strip() != '':
                        new_chunk.extend(now_title_stack)
                        if not self.is_title(line):
                            new_chunk.append(line)
                    else:
                        new_chunk.append(line)
                docs.append('\n'.join(new_chunk))
        return docs

    def remove_long_code(self, lines, max_len):
        new_lines = []
        code = ''
        is_code = False
        for line in lines:
            line = self.strip_line(line)
            if line.startswith('```'):
                is_code = not is_code

            if is_code or line.startswith('```'):
                code = code + line
            else:
                if len(code) > 0 and self.count_token(code) <= max_len:
                    new_lines.append(code)
                new_lines.append(line)
                code = ''
        return new_lines

    def count_token(self, doc):
        # doc_len = len(re.findall(r'\w+', doc)) + len(re.findall(r'[^\w\s]', doc)) + len(re.findall(r'\n', doc)) // 4
        doc_len = len(doc) // 3
        return doc_len

    def per_non_eng(self, text):
        left = re.sub(r'[_]', '', text).strip()
        left = re.sub(r'[^\w\s]', '', left).strip()
        left = re.sub(r'[0-9]', '', left).strip()
        left = re.sub(r'[a-zA-Z]', '', left).strip()
        per = len(left) / len(text)
        return per

    def strip_line(self, l):
        l = re.sub(r'<(.*?)>', '', l)
        return l.lstrip()

    def get_last_level(self, now_title_stack):
        if len(now_title_stack) > 0:
            return self.get_level(now_title_stack[-1])
        else:
            return 0

    def get_level(self, line):
        return len(re.findall('#', line.split(' ')[0]))

    def is_title(self, line):
        return line.split('# ')[0].replace('#', '') == ''


if __name__ == '__main__':
    qg = QuestionGenerator()
    file_path = 'your test doc path'
    with open(file_path, 'r') as f:
        f_doc = f.read()
        qg.generate_qa(f_doc, 'your project name')
