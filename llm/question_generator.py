import os
import re
from typing import Optional, List
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import chatai_configs


class QuestionGenerator:
    '''Use LLM to generate potential questions given document.'''
    model_name: str = chatai_configs.get('model_name', 'gpt-3.5-turbo')
    temperature: float = chatai_configs.get('temperature', 0.0)
    openai_api_key: Optional[str] = chatai_configs.get('openai_api_key', os.getenv('OPENAI_API_KEY'))
    max_tokens: Optional[int] = chatai_configs.get('max_tokens', None)

    openai.api_key = openai_api_key

    def generate_qa(self, doc: str, project: str, num: int =20, chunk_size: int = 300):
        max_doc = chunk_size
        docs = self.split_doc(doc, max_doc)
        q_doc = []
        for doc_chunk in docs:   
            messages = self.build_llm_input(doc_chunk, project, num)
            resp = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
            )

            questions = self.parse_llm_output(resp)
            for q in questions:
                q_doc.append((q, doc_chunk))
                          
        return q_doc

    def build_llm_input(self, doc: str, project: str, num: int = 20) -> List[dict]:
        system_prompt = f'''Extract {num} q&a pairs for user questions from the given document in user message.
        
        Each answer should only use the given document as source.
            
        Your question list should cover all content of the document.
            
        Return questions in json format only.'''

        user_prompt = f'Doc of an open-source project {project}:\n{doc}'

        return [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

    def parse_llm_output(self, response) -> List[str]:
        '''Parse response from LLM to return a list of extracted questions'''
        content = response['choices'][0]['message']['content']
        questions = []
        for q in content.split('\n'):
                q = ('. ').join(q.split('. ')[1:])
                if q is None:
                    raise ValueError('Invalid question value: None.')
                else:
                    questions.append(q)
        total_tokens = response['usage']['total_tokens']
        if total_tokens == 4097 and not questions[-1].endswith('.'):
            del questions[-1]
        return questions


    def split_doc(self, doc: str, max_len: int) -> List[str]:
        if self.count_token(doc) < max_len:
            docs = [doc]
        else:
            lines = doc.split('\n')
            new_lines = self.remove_long_code(lines, max_len)
            docs = []
            # There is an issue for MarkdownTextSplitter, so we use RecursiveCharacterTextSplitter
            # https://github.com/hwchase17/langchain/issues/2836
            # markdown_splitter = MarkdownTextSplitter(chunk_size=max_len, chunk_overlap=0, length_function=lambda x: self.count_token(x))  # , chunk_overlap=100)
            markdown_splitter = RecursiveCharacterTextSplitter(chunk_size=max_len, chunk_overlap=0, length_function=lambda x: self.count_token(x))  # , chunk_overlap=100)
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
