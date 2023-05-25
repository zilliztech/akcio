# Vector db configs
vectordb_config = {
    'host': 'localhost',
    'port': 19530,
    'top_k': 10,
}

# Scalar db configs
scalardb_config = {
    'host': 'localhost',
    'port': 9200,
    # 'ca_certs': 'path/to/ca_certs',
    'user': 'elastic',
    'password': 'es_password_goes_here'
}

# Memory db configs
memorydb_config = {
    'connect_str': 'postgresql://postgres:postgres@localhost/chat_history'
}
