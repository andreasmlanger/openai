"""
Simple app using the OpenAI Image Generation API
Billing: https://platform.openai.com/account/billing/overview
"""

from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

# Specify GPT version: 3 (3.5) or 4
V = 4

# Define DALL-E model and respective API key
MODEL = 'dall-e-2' if V == 3 else 'dall-e-3'
OPENAI_API_KEY = os.environ.get(f'OPENAI_API_KEY_{V}')

API_ENDPOINT = 'https://api.openai.com/v1/images/generations'
NUM_COMPLETIONS = 1  # number of images


def main():
    print('\033[93m' + 'Hi there! Please type your prompt below and press ENTER:' + '\033[38m')
    while True:
        data = {
            'model': MODEL,
            'prompt': input(),  # prompt to send to ChatGPT
            'n': NUM_COMPLETIONS,
            'size': '1024x1024',
        }

        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            for data in response_data['data']:
                print('Generated image URL:', data['url'])
        else:
            print('Error:', response.status_code, response.text)


if __name__ == '__main__':
    main()
