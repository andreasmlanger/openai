# OpenAI

A collection of scripts using OpenAI's Completion and Assistant APIs to create useful chatbots and services.

### OpenAI Text Generation Tools

OpenAI offers a comprehensive suite of tools that leverage a pre-trained natural language model for text generation. These tools are designed to facilitate a wide range of applications, from automated communication to content creation. Below is an overview of the key tools available:

### Tools Overview

- **GPT (Generative Pre-trained Transformer)**
  - **Description**: Capable of understanding and generating natural language text. These models are highly versatile and can be employed for creating chatbots, performing translations, and more.
  
- **Whisper**
  - **Description**: Specialized in understanding spoken language. It provides functionalities for transcribing voice recordings and translating spoken words into different languages.

- **Text-to-Speech (TTS)**
  - **Description**: Converts textual information into spoken words, enabling applications that require oral communication or support for visually impaired users.

### Requirements

- **Python:** Ensure Python is installed on your system.
- **OpenAI Developer Account:** You must have a developer account with OpenAI. Create one on the [API signup page](https://platform.openai.com/signup) if you haven't already.
- **Secret API Key:** Obtain a secret API key and add it to the `.env` file as an environmental variable.

### Contents

This directory includes three apps:

- **api_completion.py:** Minimalistic script to communicate with ChatGPT.
- **api_assistant_chat.py:** Console-based and Streamlit apps to create an assistant that leverages file retrieval to access information in provided documents. Start Streamlit using the command: `streamlit run api_assistant_chat.py` or run it directly in your IDE.
- **api_assistant_youtube.py:** Console-based and Streamlit apps to extract recipees from YouTube videos utilizing function calling. Start Streamlit using the command: `streamlit run api_assistant_youtube.py` or run it directly in your IDE.