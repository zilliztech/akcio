import os

QUERY_MODE = os.getenv('QUERY_MODE', 'osschat-search')  # options: osschat-search, rewrite_query
INSERT_MODE = os.getenv('INSERT_MODE', 'osschat-insert')  # options: osschat-insert, generate_questions

################## LLM ##################
LLM_OPTION = os.getenv('LLM_OPTION', 'openai')  # select your LLM service
LANGUAGE = 'en'  # options: en, zh
CHAT_CONFIG = {
    'openai': {
        'openai_model': 'gpt-3.5-turbo',
        'openai_api_key': None,  # will use environment  value 'OPENAI_API_KEY' if None
        'llm_kwargs': {
            'temperature': 0.2,
            # 'max_tokens': 200,
            }
    },
    'llama_2': {
        'llama_2_model': 'llama-2-13b-chat',
        'llm_kwargs':{
            'temperature': 0.2,
            'max_tokens': 200,
            'n_ctx': 4096
        }
    },
    'ernie': {
        'ernie_api_key': None, # If None, use environment  value 'ERNIE_API_KEY'
        'ernie_secret_key': None, # If None, use environment value 'ERNIE_SECRET_KEY'
        'llm_kwargs': {}
    },
    'minimax': {
        'minimax_model': 'abab5-chat',
        'minimax_api_key': None, # If None, use environment value 'MINIMAX_API_KEY'
        'minimax_group_id': None, # If None, use environment value 'MINIMAX_GROUP_ID'
        'llm_kwargs': {}
    },
    'dolly': {
        'dolly_model': 'databricks/dolly-v2-3b',
        'llm_kwargs': {'device': 'auto'}
    },
    'skychat': {
        'skychat_api_host': None, # If None, use default value 'sky-api.singularity-ai.com'
        'skychat_app_key': None, # If None, use environment value 'SKYCHAT_APP_KEY'
        'skychat_app_secret': None  # If None, use environment value 'SKYCHAT_APP_SECRET'
    },
    'dashscope': {
        'dashscope_model': 'qwen-plus-v1',
        'dashscope_api_key': None  # If None, use environment value 'DASHSCOPE_API_KEY'
    },
    'chatglm':{
        # 'chatglm_model': 'chatglm_130b',
        'chatglm_model': 'chatglm_std',
        'chatglm_api_key': None  # If None, use environment value 'ZHIPUAI_API_KEY'
    }
}


################## Embedding ##################
TEXTENCODER_CONFIG = {
    'model': 'multi-qa-mpnet-base-cos-v1',
    'device': -1, # -1 will use cpu
    'norm': True,
    'dim': 768
}


################## Store ##################
TEMP_DIR = './tmp'
USE_SCALAR = True if os.getenv('USE_SCALAR', 'False').lower() == 'true' else False

# Vector db configs
VECTORDB_CONFIG = {
    'connection_args': {
        'uri': os.getenv('MILVUS_URI', 'https://localhost:19530'),
        'user': os.getenv('MILVUS_USER', ''),
        'password': os.getenv('MILVUS_PASSWORD', ''),
        'secure': True if os.getenv('MILVUS_SECURE', 'False').lower() == 'true' else False
        },
    'top_k': 5,
    'threshold': 0,
    'index_params': {
        'metric_type': 'IP',
        'index_type': 'IVF_FLAT',
        'params': {'nlist': 1024}
        }
}

# Scalar db configs
SCALARDB_CONFIG = {
    'connection_args': {
        'hosts': os.getenv('ES_HOSTS', 'http://localhost:9200'),
        },
    'top_k': 3
}

for arg in ['ES_CLOUD_ID', 'ES_CA_CERTS', 'ES_CA_CERTS']:
    arg_k = arg.replace('ES_', '').lower()
    arg_v = os.getenv(arg)
    if arg_v:
        SCALARDB_CONFIG['connection_args'][arg_k] = arg_v
if os.getenv('ES_USER'):
    SCALARDB_CONFIG['connection_args']['basic_auth'] = (os.getenv('ES_USER'), os.getenv('ES_PASSWORD'))

# Memory db configs
MEMORYDB_CONFIG = {
    'connect_str': os.getenv('SQL_URI', 'postgresql://postgres:postgres@localhost/chat_history')
}


############### Rerank configs ##################
RERANK_CONFIG = {
    'rerank': True,
    'rerank_model': 'cross-encoder/ms-marco-MiniLM-L-12-v2',
    'threshold': 0.6,
    'rerank_device': -1  # -1 will use cpu
}

################## Data loader ##################
DATAPARSER_CONFIG = {
    'chunk_size': 300
}

QUESTIONGENERATOR_CONFIG = {
    'model_name': 'gpt-3.5-turbo',
    'temperature': 0,
}