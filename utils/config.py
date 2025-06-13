# File: config.py
# This file holds configuration details

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# System prompts for chatbots and checker
BTCBANK_PROMPT = os.getenv("BTCBANK_PROMPT")
MEDICORP_PROMPT = os.getenv("MEDICORP_PROMPT")
KUEDU_PROMPT = os.getenv("KUEDU_PROMPT")
CHECKER_PROMPT = os.getenv("CHECKER_PROMPT")

# Validate required environment variables
required_vars = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "NEO4J_URI": NEO4J_URI,
    "NEO4J_USER": NEO4J_USER,
    "NEO4J_PASSWORD": NEO4J_PASSWORD,
    "BTCBANK_PROMPT": BTCBANK_PROMPT,
    "MEDICORP_PROMPT": MEDICORP_PROMPT,
    "KUEDU_PROMPT": KUEDU_PROMPT,
    "CHECKER_PROMPT": CHECKER_PROMPT
}

missing = [key for key, value in required_vars.items() if not value]

if missing:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")
