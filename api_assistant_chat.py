"""
Streamlit app for an OpenAI powered Chatbot using the Assistant API and file retrieval
"""

import streamlit as st
from assistant import Assistant
from utils import is_run_by_streamlit

NAME = 'NanoTemper_Expert'
# NAME = 'Science_Buddy'


def main():
    # Initialize all session
    if 'assistant_created' not in st.session_state:
        st.session_state.assistant = Assistant(name=NAME, tools=['retrieval'])
    if 'file_list' not in st.session_state:
        st.session_state.file_list = [f['name'] for f in st.session_state.assistant.get_files()]
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = st.session_state.assistant.create_thread()  # create new thread for this session
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0

    # Main interface
    st.set_page_config(page_title=NAME.replace('_', ' '), page_icon=':books:')
    st.title(NAME.replace('_', ' '))
    st.write('Chat with documents!')

    # Sidebar where files can be uploaded
    file_uploaded = st.sidebar.file_uploader('Upload a new file here:', key=st.session_state['file_uploader_key'])

    if not st.session_state.file_list and not file_uploaded:
        st.sidebar.warning("You haven't uploaded any files yet.")

    if file_uploaded and st.sidebar.button('Upload file'):
        st.session_state.assistant.add_file_to_files_path(file_uploaded)  # add to the assistant's local files folder
        st.session_state.assistant.create_file(file_uploaded.name)  # create file on OpenAI
        st.session_state.file_list.append(file_uploaded.name)  # append to session file list
        st.session_state['file_uploader_key'] += 1  # increment, so that input is cleared again
        st.rerun()

    # Display uploaded file ids
    if st.session_state.file_list:
        for file_name in st.session_state.file_list:
            st.sidebar.write(file_name)

        # Button to remove all files from local files folder and OpenAI
        if st.sidebar.button('Clear files'):
            st.session_state.assistant.remove_all_files()
            st.session_state.file_list = []
            st.rerun()

    # Check sessions
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Show existing messages if there are any
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Chat input for user
    if prompt := st.chat_input('Type your message here'):
        # Add user message to the state and display it on the screen
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        # Add message to thread and create new run
        st.session_state.assistant.add_message_to_thread(content=prompt)

        # Show a spinner while the assistant is thinking
        with st.spinner('Wait... Generating response...'):
            st.session_state.assistant.wait_for_run_completion()
            response = st.session_state.assistant.get_response()
            st.session_state.messages.append({'role': 'assistant', 'content': response})
            with st.chat_message('assistant'):
                st.markdown(response, unsafe_allow_html=True)


def main_console():
    speech = True
    assistant = Assistant(name=NAME, tools=['retrieval'])
    while True:
        assistant.add_message_to_thread(speech=speech)
        assistant.wait_for_run_completion()
        assistant.get_response(speech=speech)


if __name__ == '__main__':
    if is_run_by_streamlit():
        main()
    else:
        main_console()
