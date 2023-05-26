import re
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain.docstore.document import Document as LCDocument


class MarkDownSplitter(TextSplitter):
    def split_text(self, text: str) -> List[str]:
        if self.count_token(text) < self._chunk_size:
            texts = [text]
        else:
            lines = text.split('\n')
            new_lines = self.remove_long_code(lines)
            markdown_splitter = RecursiveCharacterTextSplitter(chunk_size=self._chunk_size, chunk_overlap=0,
                                                               length_function=lambda x: self.count_token(x))
            documents = markdown_splitter.create_documents(['\n'.join(new_lines)])
            texts = self._keep_parent_title(documents)
        return texts

    def remove_long_code(self, lines: List[str]) -> List[str]:
        new_lines = []
        code = ''
        is_code = False
        for line in lines:
            line = self._strip_line(line)
            if line.startswith('```'):
                is_code = not is_code

            if is_code or line.startswith('```'):
                code = code + line
            else:
                if len(code) > 0 and self.count_token(code) <= self._chunk_size:
                    new_lines.append(code)
                new_lines.append(line)
                code = ''
        return new_lines

    def _keep_parent_title(self, documents: List[LCDocument]) -> List[str]:
        docs = []
        now_title_stack = []
        for doc_chunk in documents:
            new_chunk = []
            lines = doc_chunk.page_content.split('\n')
            for inner_idx, line in enumerate(lines):
                if line.strip() == '':
                    continue
                if self._is_title(line):
                    now_head_level = self._get_level(line)
                    last_level_in_stack = self._get_last_level(now_title_stack)
                    while now_head_level <= last_level_in_stack:
                        now_title_stack.pop()
                        last_level_in_stack = self._get_last_level(now_title_stack)
                    now_title_stack.append(line)
                if inner_idx == 0 and line.strip() != '':
                    new_chunk.extend(now_title_stack)
                    if not self._is_title(line):
                        new_chunk.append(line)
                else:
                    new_chunk.append(line)
            docs.append('\n'.join(new_chunk))
        return docs

    def count_token(self, doc):  # todo
        # doc_len = len(re.findall(r'\w+', doc)) + len(re.findall(r'[^\w\s]', doc)) + len(re.findall(r'\n', doc)) // 4
        doc_len = len(doc) // 3
        return doc_len

    def _strip_line(self, l):
        l = re.sub(r'<(.*?)>', '', l)
        return l.lstrip()

    def _get_last_level(self, now_title_stack):
        if len(now_title_stack) > 0:
            return self._get_level(now_title_stack[-1])
        else:
            return 0

    def _get_level(self, line):
        return len(re.findall('#', line.split(' ')[0]))

    def _is_title(self, line):
        return line.split('# ')[0].replace('#', '') == ''
