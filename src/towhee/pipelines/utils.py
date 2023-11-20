from towhee import ops


def get_llm_op(config):
    if config.llm_src.lower() == 'openai':
        return ops.LLM.OpenAI(model_name=config.openai_model, api_key=config.openai_api_key, **config.llm_kwargs)
    if config.llm_src.lower() == 'dolly':
        return ops.LLM.Dolly(model_name=config.dolly_model, **config.llm_kwargs)
    if config.llm_src.lower() == 'ernie':
        return ops.LLM.Ernie(model_name=config.ernie_model, eb_api_type=config.eb_api_type,
                             eb_access_token=config.eb_access_token, **config.llm_kwargs)
    if config.llm_src.lower() == 'minimax':
        return ops.LLM.MiniMax(model=config.minimax_model, api_key=config.minimax_api_key, group_id=config.minimax_group_id, **config.llm_kwargs)
    if config.llm_src.lower() == 'dashscope':
        return ops.LLM.DashScope(model=config.dashscope_model, api_key=config.dashscope_api_key, **config.llm_kwargs)
    if config.llm_src.lower() == 'skychat':
        return ops.LLM.SkyChat(
            model=config.skychat_model, api_host=config.skychat_api_host,
            app_key=config.skychat_app_key, app_secret=config.skychat_app_secret, **config.llm_kwargs)
    if config.llm_src.lower() == 'chatglm':
        return ops.LLM.ZhipuAI(model_name=config.chatglm_model, api_key=config.chatglm_api_key, **config.llm_kwargs)
    if config.llm_src.lower() == 'llama_2':
        return ops.LLM.Llama_2(config.llama_2_model, **config.llm_kwargs)

    raise RuntimeError('Unknown llm source: [%s], only support openai, dolly and ernie' % (config.llm_src))


def get_embedding_op(config):
    if config.embedding_device == -1:
        device = 'cpu'
    else:
        device = config.embedding_device

    _hf_models = ops.sentence_embedding.transformers().get_op().supported_model_names()  # pylint: disable=C0103
    _openai_models = ['text-embedding-ada-002', 'text-similarity-davinci-001',  # pylint: disable=C0103
                    'text-similarity-curie-001', 'text-similarity-babbage-001',
                    'text-similarity-ada-001']

    if config.embedding_model in _hf_models:
        return ops.sentence_embedding.transformers(model_name=config.embedding_model, device=device)
    elif config.embedding_model in _openai_models:
        return ops.sentence_embedding.openai(model_name=config.embedding_model, api_key=config.openai_api_key)
    else:
        return ops.sentence_embedding.sbert(model_name=config.embedding_model, device=device)

def data_loader(path):
    if path.endswith('pdf'):
        op = ops.data_loader.pdf_loader()
    elif path.endswith(('xls', 'xslx')):
        op = ops.data_loader.excel_loader()
    elif path.endswith('ppt'):
        op = ops.data_loader.powerpoint_loader()
    else:
        op = ops.text_loader()
    return op(path)
