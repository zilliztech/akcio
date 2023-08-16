import sys
import os
from towhee import AutoPipes, pipe

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import get_llm_op  # pylint: disable=C0413


REWRITE_TEMP = '''
如果 NOW QUESTION 里有代词，要把代词替换成 HISTORY 里对应的词。补全最后一轮的内容，下面开始：
-------------------
HISTORY:
[]
NOW QUESTION: 你好吗？
有代词吗: 无 => 思考: 所以 OUTPUT QUESTION 与 NOW QUESTION 相同 => OUTPUT QUESTION: 你好吗？
-------------------
HISTORY:
[Q: Milvus是矢量数据库吗？
A: 是的，Milvus 是一个矢量数据库。]
NOW QUESTION: 如何使用它？
有代词吗: 有,代词是“它” => 思考: 我需要在 NOW QUESTION 中将“它”替换为“Milvus” => OUTPUT QUESTION: 如何使用Milvus？
-------------------
HISTORY:
[]
NOW QUESTION: 它有什么特点呢？
有代词吗: 有,代词是“它” => 思考: 我需要替换 NOW QUESTION 中的“它”，但我在HISTORY中找不到单词来替换它，所以 OUTPUT QUESTION 与 NOW QUESTION 相同。=> OUTPUT QUESTION: 它有什么特点呢？
-------------------
HISTORY:
[Q: 什么是 PyTorch？
A: PyTorch 是一个 Python 开源机器学习库。它为构建和训练深度神经网络提供了灵活高效的框架。
Q: 什么是TensorFlow？
A: TensorFlow 是一个开源机器学习框架。它提供了一套全面的工具、库和资源，用于构建和部署机器学习模型。]
NOW QUESTION: 它们之间有什么区别？
有代词吗: 有,代词是“它们” => 思考: 我需要在 NOW QUESTION 中将“它们”替换为“PyTorch 和 Tensorflow”。 => OUTPUT QUESTION: PyTorch 和 Tensorflow 有什么区别？
-------------------
HISTORY:
[{history_str}]
NOW QUESTION: {question}
有代词吗: '''

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
        raw_ret = raw_ret.replace('&gt;', '>')
        new_question = raw_ret.split('=> OUTPUT QUESTION: ')[1].split('-------------------')[0]
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
