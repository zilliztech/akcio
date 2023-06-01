import os

# Vector db configs
vectordb_config = {
    'connection_args': {
        'host': os.getenv('MILVUS_HOST', 'localhost'),
        'port': os.getenv('MILVUS_PORT', '19530'),
        },
        'top_k': 10,
        'index_params': {
            'metric_type': 'IP',
            'index_type': 'IVF_FLAT',
            'params': {'nlist': 1024}
            }
}

# Scalar db configs
scalardb_config = {
    'connection_args': {
        'hosts': os.getenv('ES_HOSTS', 'https://localhost:9200'),
        'ca_certs': os.getenv('ES_CA_CERTS', None),
        'basic_auth': (os.getenv('ES_USER', 'user_name'), os.getenv('ES_PASSWORD', 'es_password'))
        },
}

# Memory db configs
memorydb_config = {
    'connect_str': os.getenv('PG_URI', 'postgresql://postgres:postgres@localhost/chat_history')
}
