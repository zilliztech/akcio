import os
import sys
from towhee import pipe, ops

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import ( # pylint: disable=C0413
    LLM_OPTION, CHAT_CONFIG
)

llm_config = CHAT_CONFIG[LLM_OPTION]
model_name = llm_config[f'{LLM_OPTION}_model']
if LLM_OPTION == 'openai':
    llm_op = ops.LLM.OpenAI(model_name=model_name, api_key=llm_config['openai_api_key'], **llm_config['llm_kwargs'])
elif LLM_OPTION == 'llama_2':
    llm_op = ops.LLM.Llama_2(model_name, **llm_config['llm_kwargs'])
elif LLM_OPTION == 'ernie':
    llm_op = ops.LLM.Ernie(api_key=llm_config['ernie_api_key'],
                           secret_key=llm_config['ernie_secret_key'], **llm_config['llm_kwargs'])
elif LLM_OPTION == 'minimax':
    llm_op = ops.LLM.MiniMax(model=model_name,
                             api_key=llm_config['minimax_api_key'],
                             group_id=llm_config['minimax_group_id'], **llm_config['llm_kwargs'])
elif LLM_OPTION == 'dashscope':
    llm_op = ops.LLM.DashScope(model=model_name, api_key=llm_config['dashscope_api_key'], **llm_config['llm_kwargs'])
elif LLM_OPTION == 'skychat':
    llm_op = ops.LLM.SkyChat(
        model=model_name, api_host=llm_config['skychat_api_host'],
        app_key=llm_config['skychat_app_key'], app_secret=llm_config['skychat_app_secret'], **llm_config['llm_kwargs'])
elif LLM_OPTION == 'chatglm':
    llm_op = ops.LLM.ZhipuAI(model_name=model_name, api_key=llm_config['chatglm_api_key'], **llm_config['llm_kwargs'])
elif LLM_OPTION == 'dolly':
    llm_op = ops.LLM.Dolly(model_name=model_name, **llm_config['llm_kwargs'])

def build_prompt(question: str, history: list = []):  # pylint: disable=W0102
    if not history:
        history_str = ''
    output_str = ''
    for qa in history:
        output_str += f'Q: {qa[0]}\n'
        output_str += f'A: {qa[1]}\n'
    history_str = output_str.strip()
    prompt = f'''
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
[Q: 今天是周几?
A: 今天是周五。
NOW QUESTION: 明天是周末吗？
NEED COREFERENCE RESOLUTION: Yes => THOUGHT: 我需要在now question中补充“今天是周五”。 => OUTPUT QUESTION: 今天是周五，明天是周末吗？
]
-------------------
HISTORY:
[{history_str}]
NOW QUESTION: {question}
NEED COREFERENCE RESOLUTION: '''
    return [({'question': prompt})]


rewrite_query = (
    pipe.input('question', 'history')
        .map(('question', 'history'), 'prompt', build_prompt)
        .map('prompt', 'answer', llm_op)
        .output('answer')
)
