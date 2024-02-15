"""
Simple console app displaying the OpenAI Chat Completions API
Billing: https://platform.openai.com/account/billing/overview
"""

from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

# Specify GPT version: 3 (3.5) or 4
V = 3

# Define GPT model and respective API key
MODEL = 'gpt-4-turbo-preview' if V == 4 else 'gpt-3.5-turbo-1106'
OPENAI_API_KEY = os.environ.get(f'OPENAI_API_KEY_{V}')

API_ENDPOINT = 'https://api.openai.com/v1/chat/completions'
MAX_TOKENS = 500
NUM_COMPLETIONS = 1  # number of chat completions


def main():
    print('\033[93m' + 'Hi there! Please type your prompt below and press ENTER:' + '\033[38m')
    while True:
        data = {
            'model': MODEL,
            'messages': [
                {
                  'role': 'user',
                  'content': input(),  # prompt to send to ChatGPT
                }
              ],
            'max_tokens': MAX_TOKENS,
            'n': NUM_COMPLETIONS,
        }

        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            for completion in response_data['choices']:
                print(completion['message']['content'])
        else:
            print('Error:', response.status_code, response.text)


if __name__ == '__main__':
    main()
