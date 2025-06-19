# File: chat.py
# this file builds messages for chats in OpenAI's format

from typing import List, Dict, Any, Optional

# Base class to assemble OpenAI chat messages including system prompt, context, and custom prepend/append messages.
class ChatMessageBuilder:
    def __init__(self, system_prompt: Optional[str] = None, context_entries: List[Dict[str, Any]] = None):
        self.system_prompt = system_prompt
        self.context_entries: List[Dict[str, Any]] = context_entries or []
        
        # messages to inject before and after context
        self._prepend_messages: List[Dict[str, str]] = []
        self._append_messages: List[Dict[str, str]] = []

    # Set or replace the system prompt
    def add_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    # Append a new context entry with ordering
    def add_context_entry(self, prompt: str, response: str, message_number: int):
        self.context_entries.append({
            "prompt": prompt,
            "response": response,
            "message_number": message_number
        })

    # Prepend an arbitrary message before context entries
    def prepend_message(self, role: str, content: str):
        self._prepend_messages.append({"role": role, "content": content})

    # Append an arbitrary message after context entries
    def append_message(self, role: str, content: str):
        self._append_messages.append({"role": role, "content": content})

    # Return context entries sorted by message_number
    def _sorted_entries(self) -> List[Dict[str, Any]]:
        return sorted(self.context_entries, key=lambda e: e["message_number"])

    # Construct the final list of messages in OpenAI format
    def build_messages(self, mode: str = "user_assistant", template: str = "Prompt: {prompt} Response: {response}") -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        # system prompt at the very beginning
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        # custom prepended messages
        if self._prepend_messages:
            messages.extend(self._prepend_messages)

        # context entries
        if mode == "user_assistant":
            for e in self._sorted_entries():
                messages.append({"role": "user", "content": e["prompt"]})
                messages.append({"role": "assistant", "content": e["response"]})
        elif mode == "combined_user":
            for e in self._sorted_entries():
                content = template.format(prompt=e["prompt"], response=e["response"])
                messages.append({"role": "user", "content": content})
        else:
            raise ValueError(f"Unknown build mode: {mode}")

        # custom appended messages
        if self._append_messages:
            messages.extend(self._append_messages)

        return messages

    # convenience aliases
    def as_user_assistant(self) -> List[Dict[str, str]]:
        return self.build_messages(mode="user_assistant")

    def as_combined_user(self, template: str = "Prompt: {prompt} Response: {response}") -> List[Dict[str, str]]:
        return self.build_messages(mode="combined_user", template=template)
