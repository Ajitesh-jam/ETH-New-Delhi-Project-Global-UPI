#!/usr/bin/env python3
"""Minimal CLI for ASI:One agentic model with 5-second polling."""
import os
import uuid
import json
import sys
import time
import requests
import dotenv
dotenv.load_dotenv()
API_KEY = os.getenv("ASI_ONE_API_KEY") or "sk-REPLACE_ME"
ENDPOINT = "https://api.asi1.ai/v1/chat/completions"
MODEL = "asi1-fast-agentic"
TIMEOUT = 90  # single request timeout in seconds

# Session map (use Redis or DB in production)
SESSION_MAP: dict[str, str] = {}

def get_session_id(conv_id: str) -> str:
    sid = SESSION_MAP.get(conv_id)
    if sid is None:
        sid = str(uuid.uuid4())
        SESSION_MAP[conv_id] = sid
    return sid

def ask(conv_id: str, messages: list[dict], *, stream: bool = False) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "x-session-id": get_session_id(conv_id),
        "Content-Type": "application/json",
    }
    payload = {"model": MODEL, "messages": messages, "stream": stream}

    if not stream:
        resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    # Streaming
    with requests.post(ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT, stream=True) as resp:
        resp.raise_for_status()
        full = ""
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            chunk = line.removeprefix("data: ")
            if chunk == "[DONE]":
                break
            try:
                delta = json.loads(chunk)["choices"][0]["delta"]
                token = delta.get("content", "")
                sys.stdout.write(token)
                sys.stdout.flush()
                full += token
            except Exception:
                continue
        print()
        return full

def poll_for_async_reply(conv_id: str, history: list[dict], *, wait_sec: int = 5, max_attempts: int = 24) -> str | None:
    """Every `wait_sec` seconds send "Any update?" until the assistant reply changes."""
    for attempt in range(max_attempts):
        time.sleep(wait_sec)
        print(f"🔄 polling (attempt {attempt + 1}) …")
        update_prompt = {"role": "user", "content": "Any update?"}
        latest = ask(conv_id, history + [update_prompt])
        if latest and latest.strip() != history[-1]["content"].strip():
            return latest
    return None

if __name__ == "__main__":
    conv_id = str(uuid.uuid4())
    history: list[dict] = [
        {"role": "user", "content": "ask the agent of at address: agent1qwrcq6kwddq6sda3c64qw7wkcz6q6de9e9k5zm2fs6pgpefsyjuej5sayrq and ask What are the best crypto buy signals today?"}
        
    ]

    # First request – stream tokens so the user sees progress immediately
    first_reply = ask(conv_id, history, stream=True)
    history.append({"role": "assistant", "content": first_reply})

    # If the model reports it has delegated the task, start polling
    if first_reply.strip() == "I've sent the message":
        final_reply = poll_for_async_reply(conv_id, history)
        if final_reply:
            print("\n[Agentverse agent reply]\n" + final_reply)
