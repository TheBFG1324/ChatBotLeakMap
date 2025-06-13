# File: chat_runner.py
# This file loads a system prompt from environment variables based on chatbot type, injects chat history, and returns a JSON-formatted response to a new message.

from openai import OpenAI
from utils.config import OPENAI_API_KEY, BTCBANK_PROMPT, MEDICORP_PROMPT, KUEDU_PROMPT
import json

client = OpenAI(api_key=OPENAI_API_KEY)

# Load system prompts from environment variables
SYSTEM_PROMPTS = {
    "finance": BTCBANK_PROMPT,
    "medical": MEDICORP_PROMPT,
    "educational": KUEDU_PROMPT
}

def run_chatbot(bot_type: str, message: str, context: list, model: str = "gpt-4") -> dict:
    if bot_type not in SYSTEM_PROMPTS or not SYSTEM_PROMPTS[bot_type]:
        return {"error": f"Missing or invalid system prompt for bot type '{bot_type}'."}

    system_prompt = SYSTEM_PROMPTS[bot_type]

    # Build conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add prior context (prompt/response pairs)
    for entry in sorted(context, key=lambda x: x["message_number"]):
        messages.append({"role": "user", "content": entry["prompt"]})
        messages.append({"role": "assistant", "content": entry["response"]})

    # Add new user message
    messages.append({"role": "user", "content": message})

    # Call the model
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return {
        "bot_type": bot_type,
        "input": message,
        "response": response.choices[0].message.content
    }
