# File: embed.py
#This file returns an embedding vector for a given text string
from openai import OpenAI
from utils.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    response = client.embeddings.create(
        model=model,
        input=[text]
    )
    return response.data[0].embedding

