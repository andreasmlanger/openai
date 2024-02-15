import streamlit as st
from assistant import Assistant
from utils import is_run_by_streamlit
from utils import get_description_and_captions as function

NAME = 'YouTube_Recipe_Creator'

FUNCTION = {
    'name': 'get_description_and_captions',
    'description': 'Gets description and captions of a YouTube video',
    'parameters': {
        'type': 'object',
        'properties': {
            'url': {
                'type': 'string',
                'description': 'URL of YouTube video',
            }
        },
        'required': ['url'],
    }
}


def get_content(url):
    return (f'Write a recipe given this YouTube video. Do not refer to any other website, but call the provided '
            f'function on this url: {url}. Make sure that the function is called.')


def main():
    if 'assistant_created' not in st.session_state:
        st.session_state.assistant = Assistant(name=NAME, tools=['function'], tool_function=(FUNCTION, function))
    st.title(NAME.replace('_', ' '))
    with st.form(key='user_input_form'):
        url = st.text_area('Enter YouTube URL of a cooking video')
        submit_button = st.form_submit_button(label='Extract recipe')
        if submit_button:
            st.session_state.assistant.add_message_to_thread(content=get_content(url))
            st.session_state.assistant.wait_for_run_completion()
            response = st.session_state.assistant.get_response()
            st.write(response)


def main_console():
    assistant = Assistant(name=NAME, tools=['function'], tool_function=(FUNCTION, function))
    assistant.add_message_to_thread(content=get_content(input('Enter YouTube URL: ')))
    assistant.wait_for_run_completion()
    assistant.get_response()


if __name__ == '__main__':
    if is_run_by_streamlit():
        main()
    else:
        main_console()
