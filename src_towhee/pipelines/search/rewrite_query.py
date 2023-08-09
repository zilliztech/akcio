import sys
import os
from towhee import AutoPipes, pipe

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import get_llm_op  # pylint: disable=C0413


REWRITE_TEMP = '''
HISTORY:
[]
NOW QUESTION: Hello, how are you?
NEED COREFERENCE RESOLUTION: No => THOUGHT: So output question is the same as now question. => OUTPUT QUESTION: Hello, how are you?
-------------------
HISTORY:
[Q: Is Milvus a vector database?
A: Yes, Milvus is a vector database.]
NOW QUESTION: How to use it?
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: I need to replace 'it' with 'Milvus' in now question. => OUTPUT QUESTION: How to use Milvus?
-------------------
HISTORY:
[]
NOW QUESTION: What is the features of it?
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: I need to replace 'it' in now question, but I can't find a word in history to replace it, so the output question is the same as now question. => OUTPUT QUESTION: What is the features of it?
-------------------
HISTORY:
[Q: What is PyTorch?
A: PyTorch is an open-source machine learning library for Python. It provides a flexible and efficient framework for building and training deep neural networks. 
Q: What is Tensorflow?
A: TensorFlow is an open-source machine learning framework. It provides a comprehensive set of tools, libraries, and resources for building and deploying machine learning models.]
NOW QUESTION: What is the difference between them?
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: I need replace 'them' with 'PyTorch and Tensorflow' in now question. => OUTPUT QUESTION: What is the different between PyTorch and Tensorflow?
-------------------
HISTORY:
[{history_str}]
NOW QUESTION: {question}
NEED COREFERENCE RESOLUTION: '''

def build_prompt(question: str, history: list = []):  # pylint: disable=W0102
    if not history:
        history_str = ''
    output_str = ''
    for qa in history:
        output_str += f'Q: {qa[0]}\n'
        output_str += f'A: {qa[1]}\n'
    history_str = output_str.strip()
    prompt = REWRITE_TEMP.format(question=question, history_str=history_str)
    return [({'question': prompt})]

def parse_raw_ret(raw_ret, question):
    try:
        new_question = raw_ret.split('=> OUTPUT QUESTION: ')[1]
    except:  # pylint: disable=W0702
        new_question = question
    return new_question

def custom_pipeline(config):
    llm_op = get_llm_op(config)
    chat = AutoPipes.pipeline('osschat-search', config=config)
    p = (
        pipe.input('question', 'history', 'project')
            .map(('question', 'history'), 'prompt', build_prompt)
            .map('prompt', 'new_question', llm_op)
            .map(('new_question', 'question'), 'new_question', parse_raw_ret)
            .map(('new_question', 'history', 'project'), 'answer', chat)
            .output('new_question', 'answer')
    )
    return p
