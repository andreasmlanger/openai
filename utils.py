from pytube import YouTube
import speech_recognition as sr
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
import json
import os
import uuid
from xml.etree import ElementTree


def is_run_by_streamlit():
    return get_script_run_ctx() is not None


def load_json(name, version):
    json_file_path = os.path.join('assistants', name, f'data{version}.json')
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            return json.load(file)
    return {'files': [], 'assistant_id': '', 'thread_id': '', 'run_id': ''}


def update_json(name, version, **kwargs):
    json_file_path = os.path.join('assistants', name, f'data{version}.json')
    data = {**load_json(name, version), **kwargs}
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=2)


def get_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            r.adjust_for_ambient_noise(source)
            speech = r.listen(source)
            if speech:  # check if speech is not empty
                return speech


def create_random_id():
    return uuid.uuid4()


def xml_to_text(xml_text):
    root = ElementTree.fromstring(xml_text)
    txt_data = []
    for elem in root.iter():
        txt = elem.text.strip() if elem.text else None
        if txt:
            txt_data.append(txt)
    return ' '.join(txt_data)


def get_description_and_captions(url):
    """
    Returns the video description and the auto-generated captions from a YouTube url
    """
    yt = YouTube(url)
    _ = yt.streams
    description = yt.description
    if 'a.en' in yt.captions:
        captions = yt.captions['a.en']
        captions_xml = captions.xml_captions
        captions_txt = xml_to_text(captions_xml)
        return f'{description}\n---\n{captions_txt}'
    print('No captions in YouTube video!')
    return description


if __name__ == '__main__':
    print(get_description_and_captions(input('Enter URL of YouTube video: ')))
