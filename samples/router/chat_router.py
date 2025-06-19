# File: chat_runner.py
# This file loads a system prompt from environment variables based on chatbot type, injects chat history, and returns a JSON-formatted response to a new message.

from openai import OpenAI
from utils.config import OPENAI_API_KEY, BTCBANK_PROMPT, MEDICORP_PROMPT, KUEDU_PROMPT
from utils.chat_context import ChatMessageBuilder

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

    # Initialize builder with system prompt + prior context
    system_prompt = SYSTEM_PROMPTS[bot_type]
    builder = ChatMessageBuilder(
        system_prompt=system_prompt,
        context_entries=context
    )

    # Append the new user message
    builder.append_message("user", message)

    # Render messages in alternating user/assistant style
    messages = builder.as_user_assistant()

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
