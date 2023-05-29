import os

# Vector db configs
vectordb_config = {
    'connection_args': {
        'host': 'localhost',
        'port': 19530,
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
        'ca_certs': os.getenv('ES_CA_CERTS', 'path/to/es_carts'),
        'basic_auth': (os.getenv('ES_USER', 'user_name'), os.getenv('ES_PASSWORD', 'es_password'))
        },
}

# Memory db configs
memorydb_config = {
    'connect_str': 'postgresql://postgres:postgres@localhost/chat_history'
}
