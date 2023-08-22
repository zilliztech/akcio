import uuid
import argparse
import gradio as gr

# Specify mode
parser = argparse.ArgumentParser(
    description='Start service with different modes.')
parser.add_argument('--langchain', action='store_true')
parser.add_argument('--towhee', action='store_true')

args = parser.parse_args()

USE_LANGCHAIN = args.langchain
USE_TOWHEE = args.towhee

assert (USE_LANGCHAIN and not USE_TOWHEE) or (USE_TOWHEE and not USE_LANGCHAIN), \
    'The service should start with either "--langchain" or "--towhee".'

if USE_LANGCHAIN:
    from src_langchain.operations import chat, insert, check, drop, get_history, clear_history  # pylint: disable=C0413
if USE_TOWHEE:
    from src_towhee.operations import chat, insert, check, drop, get_history, clear_history  # pylint: disable=C0413


def create_session_id():
    uid = str(uuid.uuid4())
    suid = ''.join(uid.split('-'))
    return 'sess_' + suid


def respond(session, project, query):
    _, answer = chat(session, project, query)
    history = get_history(project, session)
    if len(history) == 0 or history[-1] != (query, answer):
        history.append((query, answer))
    return history


def clear_memory(project, session):
    clear_history(project, session)
    history = get_history(project, session)
    return history


def add_project(project, data_url: str = None, data_file: object = None):
    if data_file:
        return insert(data_src=data_file.name, project=project, source_type='file')
    if data_url:
        return insert(data_src=data_url, project=project, source_type='url')


def check_project(project):
    status = check(project)
    if status['store']:
        return 'Project exists. You can upload more documents or directly start conversation.'
    else:
        return 'Project does not exist. You need to upload the first document before conversation.'


def drop_project(project):
    return drop(project)


with gr.Blocks() as demo:
    session_id = gr.State(create_session_id)

    gr.Markdown('''<h1 style="text-align: center;">Akcio Demo</h1>''')
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown('''## Project''')
            project_name = gr.Textbox(
                value='akcio_demo',
                label='Project Name',
                info='The name can contain numbers, letters, and underscores (_).'
            )
            project_status = gr.Textbox(
                value='Project Status', show_label=False)
            check_btn = gr.Button(value='Check')
            check_btn.click(
                check_project,
                inputs=[project_name],
                outputs=project_status
            )
            drop_btn = gr.Button(value='Drop')
            drop_btn.click(
                drop_project,
                inputs=project_name,
                outputs=project_status
            )

            with gr.Accordion('Add data', open=False):
                select_data_src = gr.Radio(
                    choices=['Enter URL', 'Upload File'],
                    label='Document source',
                    value='Enter URL'
                )
                source_url = gr.Textbox(label='Doc URL')
                source_file = gr.File(
                    file_types=['text', '.md', '.txt'], type='file', label='Doc File', visible=False)
                select_data_src.change(
                    lambda x: [
                        gr.update(visible=True if x == 'Enter URL' else False),
                        gr.update(visible=True if x ==
                                  'Upload File' else False),
                    ],
                    inputs=[select_data_src],
                    outputs=[source_url, source_file],
                )

                data_count = gr.Number(value=0, label='Chunk inserted')
                add_btn = gr.Button(value='Add')
                add_btn.click(
                    add_project,
                    inputs=[project_name, source_url, source_file],
                    outputs=data_count
                )

        with gr.Column(scale=2):
            gr.Markdown('''## Chat''')
            conversation = gr.Chatbot(label='conversation').style(height=500)
            question = gr.Textbox(label='question', value=None)

            send_btn = gr.Button('Send Message')
            send_btn.click(
                fn=respond,
                inputs=[
                    session_id,
                    project_name,
                    question
                ],
                outputs=conversation,
            )

            clear_btn = gr.Button('Clear Conversation')
            clear_btn.click(
                fn=clear_memory,
                inputs=[
                    project_name,
                    session_id
                ],
                outputs=conversation,
            )


if __name__ == '__main__':
    demo.queue().launch(server_name='127.0.0.1', server_port=8900, share=True)
