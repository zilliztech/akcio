import sys
import os
from towhee import pipe, ops

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import get_embedding_op, get_llm_op, data_loader  # pylint: disable=C0413


SYS_TEMP = '''Extract {num} q&a pairs for user questions from the given document in user message.
Each answer should only use the given document as source.
Your question list should cover all content of the document.
Return a list of questions only.'''

QUERY_TEMP = '''Document of project {project}:\n{doc}'''

def build_prompt(doc, project: str = '', num: int = 10):
    sys_prompt = SYS_TEMP.format(num=num)
    query_prompt = QUERY_TEMP.format(project=project, doc=doc)
    return [({'system': sys_prompt}), ({'question': query_prompt})]

def parse_output(res):
    questions = []
    for q in res.split('\n'):
        q = ('. ').join(q.split('. ')[1:])
        questions.append(q)
    return questions

def custom_pipeline(config):
    embedding_op = get_embedding_op(config)
    llm_op = get_llm_op(config)
    p = (
        pipe.input('doc', 'project')
            .map('doc', 'text', data_loader)
            .flat_map('text', 'chunk', ops.text_splitter(
                        type=config.type, chunk_size=config.chunk_size, **config.splitter_kwargs
            ))
            .map(('chunk', 'project'), 'prompt', build_prompt)
            .map('prompt', 'gen_res', llm_op)
            .flat_map('gen_res', 'gen_question', parse_output)
            .map('gen_question', 'embedding', embedding_op)
    )

    if config.embedding_normalize:
        p = p.map('embedding', 'embedding', ops.towhee.np_normalize())

    p = p.map(('project', 'chunk', 'gen_question', 'embedding'), 'milvus_res',
              ops.ann_insert.osschat_milvus(host=config.milvus_host,
                                            port=config.milvus_port,
                                            user=config.milvus_user,
                                            password=config.milvus_password,
                                            ))

    if config.es_enable:
        es_index_op = ops.elasticsearch.osschat_index(host=config.es_host,
                                                      port=config.es_port,
                                                      user=config.es_user,
                                                      password=config.es_password,
                                                      ca_certs=config.es_ca_certs,
                                                      )
        p = (
            p.map(('gen_question', 'chunk'), 'es_doc', lambda x, y: {'sentence': x, 'doc': y})
             .map(('project', 'es_doc'), 'es_res', es_index_op)
             .map(('milvus_res', 'es_res'), 'res', lambda x, y: {'milvus_res': x, 'es_res': y})
        )
    else:
        p = p.map('milvus_res', 'res', lambda x: {'milvus_res': x, 'es_res': None})

    return p.output('res')
