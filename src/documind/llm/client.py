import os
from functools import lru_cache

from dotenv import load_dotenv
from groq import Groq

from src.documind.config import LLM_MODEL

load_dotenv()


@lru_cache(maxsize=1)
def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate(messages, temperature=0):
    """Send chat messages to the LLM and return the reply text."""
    response = get_client().chat.completions.create(
        model=LLM_MODEL, messages=messages, temperature=temperature
    )
    return response.choices[0].message.content