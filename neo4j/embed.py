# File: neo4j/embed.py
# This file gets an 1536-dimensional float array embedding from text using openai's api
import openai
from utils.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Gets embedding vector from given text
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """
    Generate and return a 1536-dimensional embedding for the given text.
    """
    response = openai.Embedding.create(
        model=model,
        input=[text]
    )
    # Embedding API returns a list of embeddings; we provided one input
    embedding = response['data'][0]['embedding']
    return embedding
