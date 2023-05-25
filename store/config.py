# Vector db configs
vectordb_config = {
    'host': 'localhost',
    'port': 19530,
    'top_k': 10,
}

# Scalar db configs
scalardb_config = {
    'hosts': 'https://localhost:9200',
    # 'ca_certs': 'path/to/ca_certs',
    'basic_auth': ('user', 'password')
}

# Memory db configs
memorydb_config = {
    'connect_str': 'postgresql://postgres:postgres@localhost/chat_history'
}
