"""
Creates an assistant with files retrieval using the OpenAI Assistants API
"""

from dotenv import load_dotenv
import openai
import json
import playsound
import os
import time
from utils import load_json, update_json, get_speech, create_random_id

load_dotenv()

# Specify GPT version: 3 (3.5) or 4
V = 4

# Define GPT model and respective API key
MODEL = 'gpt-4o' if V == 4 else 'gpt-3.5-turbo-1106'
OPENAI_API_KEY = os.environ.get(f'OPENAI_API_KEY_{V}')


class Assistant:
    def __init__(self, name, tools=None, tool_function=None):
        self.name = name
        self.tools = [] if tools is None else tools
        self.tool_function = tool_function  # tuple of json and actual function object
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.files_path = os.path.join('assistants', name, 'files')
        self.instructions = self.load_instructions()
        self.check_for_new_files()
        self.vector_store_id = self.get_vector_store_id()
        self.assistant_id = self.get_assistant_id()

    def load_instructions(self):
        instructions_file = 'instructions.txt'
        path_to_instructions = os.path.join('assistants', self.name, instructions_file)
        try:
            with open(path_to_instructions, 'r') as file:
                instructions = file.read()
        except FileNotFoundError:
            print(f'No {instructions_file} found!')
            instructions = ''
        return f'{instructions} Please answer the question using the knowledge provided in the files.'

    def get_assistant_id(self):
        return load_json(name=self.name, version=V).get('assistant_id') or self.create_assistant()

    def get_vector_store_id(self):
        return load_json(name=self.name, version=V).get('vector_store_id') or self.create_vector_store()

    def create_assistant(self):
        print('Creating new OpenAI Assistant (https://platform.openai.com/assistants)')
        assistant = self.client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            model=MODEL,
            tools=self.get_tools(),
            tool_resources={'file_search': {'vector_store_ids': [self.vector_store_id]}}
        )
        update_json(name=self.name, version=V, assistant_id=assistant.id)
        print(f'Assistant with ID {assistant.id} created!')
        return assistant.id

    def get_tools(self):
        tools = []
        if 'file_search' in self.tools:
            tools.append({'type': 'file_search'})  # file_search can access uploaded files!
        if 'function' in self.tools and self.tool_function is not None:
            tools.append({'type': 'function', 'function': self.tool_function[0]})
        return tools

    def get_thread_id(self):
        return load_json(name=self.name, version=V).get('thread_id') or self.create_thread()

    def create_thread(self):
        thread = self.client.beta.threads.create()
        update_json(name=self.name, version=V, thread_id=thread.id)
        print(f'Thread with ID {thread.id} created!')
        return thread.id

    def get_files(self):
        return load_json(name=self.name, version=V).get('files')

    def check_for_new_files(self):
        if os.path.exists(self.files_path):
            existing_file_names = [f['name'] for f in self.get_files()]
            for file_name in os.listdir(self.files_path):
                if file_name not in existing_file_names:
                    self.create_file(file_name=file_name)

    def create_file(self, file_name):
        print('Creating new OpenAI file (https://platform.openai.com/files)')
        os.makedirs(self.files_path, exist_ok=True)  # make sure that folder for files exists
        file_path = os.path.join(self.files_path, file_name)
        file = self.client.files.create(
            file=open(file_path, 'rb'),
            purpose='assistants',
        )  # upload file to OpenAI embeddings
        print(f'{file_name} created!')
        update_json(name=self.name, version=V, files=self.get_files() + [{'id': file.id, 'name': file_name}])
        return file.id

    def create_vector_store(self):
        print('Creating new VectorStore')
        vector_store = self.client.beta.vector_stores.create(
            file_ids=[f['id'] for f in self.get_files()]
        )
        update_json(name=self.name, version=V, vector_store_id=vector_store.id)
        return vector_store.id

    def remove_all_files(self):
        for file in self.get_files():
            self.client.files.delete(file_id=file['id'])
            os.remove(os.path.join(self.files_path, file['name']))
            print(f"Deleted {file['name']}!")
        update_json(name=self.name, version=V, files=[])

    def add_file_to_files_path(self, file):
        file_path = os.path.join(self.files_path, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())

    def get_content(self, speech):
        if speech:
            print('Say message: ', end='')
            speech = get_speech()
            return self.speech_to_text(speech)
        return input('Add message: ')

    def add_message_to_thread(self, content='', speech=False):
        try:
            self.client.beta.threads.messages.create(
                thread_id=self.get_thread_id(),
                role='user',
                content=content or self.get_content(speech),
            )
            update_json(name=self.name, version=V, run_id=self.create_run())
        except openai.BadRequestError:
            pass  # Run hasn't finished yet

    def create_run(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.get_thread_id(),
            assistant_id=self.assistant_id,
            instructions=self.instructions,
        )
        return run.id

    def wait_for_run_completion(self):
        print(f'Waiting for run completion: ', end='')
        run_id = load_json(name=self.name, version=V).get('run_id')
        while True:
            print('#', end='')
            run = self.client.beta.threads.runs.retrieve(thread_id=self.get_thread_id(), run_id=run_id)
            if run.completed_at:
                elapsed_time_in_seconds = run.completed_at - run.created_at
                print(f' OK [Time: {elapsed_time_in_seconds} s]')
                break
            elif run.status == 'requires_action':
                print(' FUNCTION CALL ', end='')
                output = self.call_tool_function(required_actions=run.required_action.submit_tool_outputs.model_dump())
                try:
                    self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=self.get_thread_id(),
                        run_id=run_id,
                        tool_outputs=output,
                    )
                except openai.BadRequestError:
                    pass
                print('OK ', end='')
            time.sleep(5)  # pause for 5 seconds before next retrieval attempt

    def get_response(self, speech=False):
        messages = self.client.beta.threads.messages.list(thread_id=self.get_thread_id())
        last_message = messages.data[0]
        response = last_message.content[0].text.value
        if speech:
            self.text_to_speech(response)
        print(response)
        return response

    def call_tool_function(self, required_actions):
        tool_outputs = []
        for action in required_actions['tool_calls']:
            arguments = json.loads(action['function']['arguments'])
            output = self.tool_function[1](**arguments)
            tool_outputs.append({'tool_call_id': action['id'], 'output': output})
        return tool_outputs

    def speech_to_text(self, speech):
        wav_file = 'speech.wav'
        with open(wav_file, 'ab') as file:
            file.write(speech.get_wav_data())
        with open(wav_file, 'rb') as file:
            translation = self.client.audio.translations.create(
                model='whisper-1',
                file=file,
                response_format='text',
            )
        print(translation)
        os.remove(wav_file)  # clean up
        return translation

    def text_to_speech(self, text):
        audio_response = self.client.audio.speech.create(
            model='tts-1',
            voice='shimmer',
            input=text,
        )
        mp3_file = f'response_{create_random_id()}.mp3'
        audio_response.stream_to_file(mp3_file)
        playsound.playsound(mp3_file, True)
        os.remove(mp3_file)  # clean up
