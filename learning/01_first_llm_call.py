import os
from dotenv import load_dotenv
from groq import Groq

# Load the API key from the .env file
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Send one system message and one user message to the model
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant.Answer in one short sentence."},
        {"role": "user", "content": "What is a Large Language Model?"},
    ],
    temperature=0,
)

# The generated text is inside the first choice
print(response.choices[0].message.content)