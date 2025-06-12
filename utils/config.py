# File: config.py
# This file holds configuration details
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Neo4j connection details
env_uri = os.getenv("NEO4J_URI")
env_user = os.getenv("NEO4J_USER")
env_password = os.getenv("NEO4J_PASSWORD")

if not all([OPENAI_API_KEY, env_uri, env_user, env_password]):
    missing = [name for name, val in [
        ("OPENAI_API_KEY", OPENAI_API_KEY),
        ("NEO4J_URI", env_uri),
        ("NEO4J_USER", env_user),
        ("NEO4J_PASSWORD", env_password)
    ] if not val]
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

NEO4J_URI = env_uri
NEO4J_USER = env_user
NEO4J_PASSWORD = env_password
