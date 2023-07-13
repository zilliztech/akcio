import os

################## LLM ##################
LLM_OPTION = os.getenv('LLM_OPTION', 'openai')  # select your LLM service
CHAT_CONFIG = {
    'openai': {
        'openai_model': 'gpt-3.5-turbo',
        'openai_api_key': None,  # will use environment  value 'OPENAI_API_KEY' if None
        'llm_kwargs': {
            'temperature': 0.8,
            # 'max_tokens': 200,
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
        'chatglm_model': 'chatglm_130b',
        'chatglm_api_key': None  # If None, use environment value 'ZHIPUAI_API_KEY'
    }
}


################## Embedding ##################
TEXTENCODER_CONFIG = {
    'model': 'multi-qa-mpnet-base-cos-v1',
    'norm': True,
    'dim': 768
}


################## Store ##################
USE_SCALAR = os.getenv('USE_SCALAR', False)

# Vector db configs
VECTORDB_CONFIG = {
    'connection_args': {
        'uri': os.getenv('MILVUS_URI', 'https://localhost:19530'),
        'user': os.getenv('MILVUS_USER', ''),
        'password': os.getenv('MILVUS_PASSWORD', ''),
        'secure': True if os.getenv('MILVUS_SECURE', 'False').lower() == 'true' else False
        },
    'top_k': 10,
    'threshold': 0.6,
    'index_params': {
        'metric_type': 'IP',
        'index_type': 'IVF_FLAT',
        'params': {'nlist': 1024}
        }
}

# Scalar db configs
SCALARDB_CONFIG = {
    'connection_args': {
        'hosts': os.getenv('ES_HOSTS', 'https://localhost:9200'),
        'ca_certs': os.getenv('ES_CA_CERTS', None),
        'basic_auth': (os.getenv('ES_USER', 'user_name'), os.getenv('ES_PASSWORD', 'es_password'))
        },
}

# Memory db configs
MEMORYDB_CONFIG = {
    'connect_str': os.getenv('SQL_URI', 'postgresql://postgres:postgres@localhost/chat_history')
}


############### Rerank configs ##################
RERANK_CONFIG = {
    'rerank': True,
    'rerank_model': 'cross-encoder/ms-marco-MiniLM-L-12-v2',
    'threshold': 0.6
}

################## Data loader ##################
DATAPARSER_CONFIG = {
    'chunk_size': 300
}

QUESTIONGENERATOR_CONFIG = {
    'model_name': 'gpt-3.5-turbo',
    'temperature': 0,
}