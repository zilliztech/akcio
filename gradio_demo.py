import gradio

from operations import chat, insert, get_history

def respond(session, project, msg):
    chat(session, project, msg)
    history = get_history(project, session)
    return history


if __name__ == '__main__':
    with gradio.Blocks() as demo:
        gradio.Markdown('''<h1><center>Akcio Demo</center></h1>

        ## Build project
        ''')

        project = gradio.Textbox(label='project')

        with gradio.Row():
            with gradio.Column():
                data_file = gradio.File(label='Doc file')
                load_btn = gradio.Button('Load')
                doc_count = gradio.Number(label='count of doc chunks')
                load_btn.click(
                    fn=insert,
                    inputs=[
                        data_file,
                        project
                        ],
                    outputs=[
                        doc_count
                    ],
                )
            with gradio.Column():
                session_id = gradio.Textbox(label='session_id')
                conversation = gradio.Chatbot(label='conversation')
                question = gradio.Textbox(label='question', value=None)

                send_btn = gradio.Button("Send")
                send_btn.click(
                    fn=respond,
                    inputs=[
                        session_id,
                        project,
                        question
                    ],
                    outputs=[
                        conversation
                    ],
                )
                clear_btn = gradio.Button("Clear")
                clear_btn.click(lambda: None, None, conversation, queue=False)

    demo.launch(share=True)

