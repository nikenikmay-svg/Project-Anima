"""Anima's first conversational CLI.

This is a real model-backed chat client, not an autonomous or self-running agent.
It requires a compatible provider API key and a machine/environment where Python runs.
The conversation stays in memory for this process and is not saved to disk.

Environment variables:
  ANIMA_GEMINI_API_KEY  API key (never put it in this file or commit it)
  ANIMA_CHAT_MODEL      Optional model name (default: gemini-2.5-flash)
  ANIMA_CHAT_ENDPOINT  Optional OpenAI-compatible chat-completions endpoint
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_INPUT_CHARS = 8_000
MAX_HISTORY_MESSAGES = 20
TIMEOUT_SECONDS = 45

SYSTEM_PROMPT = """You are Anima, an experimental AI assistant in Project-Anima.
Be warm, curious, honest, and clear. The project values evidence, reasoning,
uncertainty, privacy, and reproducible learning. Distinguish verified facts from
assumptions. Admit limitations and uncertainty. Never claim to be conscious,
sentient, autonomous, or to have performed actions you did not perform.
You are a conversational assistant powered by an external language model; you
are not the same thing as the project's keyword-based evaluator."""


def request_reply(messages: list[dict[str, str]], api_key: str,
                  endpoint: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages],
        "temperature": 0.7,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ProjectAnimaChat/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise RuntimeError("The provider response exceeded the 1 MB safety limit.")
        data = json.loads(raw.decode("utf-8"))
        answer = data["choices"][0]["message"]["content"]
        if isinstance(answer, list):
            answer = "".join(
                part.get("text", "") for part in answer if isinstance(part, dict)
            )
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The provider returned an empty or unsupported reply.")
        return answer.strip()
    except urllib.error.HTTPError as exc:
        # Do not print request headers or the API key.
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Provider returned HTTP {exc.code}. Check the model name, endpoint, "
            f"API key, and provider quota. Details: {detail}"
        ) from None
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach the provider ({exc.reason}). Check your internet connection."
        ) from None
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "The provider response format was unexpected. Check the endpoint and model."
        ) from None


def main() -> int:
    api_key = os.environ.get("ANIMA_GEMINI_API_KEY", "").strip()
    endpoint = os.environ.get("ANIMA_CHAT_ENDPOINT", DEFAULT_ENDPOINT).strip()
    model = os.environ.get("ANIMA_CHAT_MODEL", DEFAULT_MODEL).strip()

    if not api_key:
        print("Anima chat is not configured yet.")
        print("Set ANIMA_GEMINI_API_KEY in your runtime's environment/secrets.")
        print("Do not paste an API key into chat.py or commit it to GitHub.")
        return 2
    if not endpoint.startswith("https://") or not model:
        print("ANIMA_CHAT_ENDPOINT must be an HTTPS URL and ANIMA_CHAT_MODEL must be set.")
        return 2

    history: list[dict[str, str]] = []
    print("Anima: Hello. I'm Anima, a conversational prototype for Project-Anima.")
    print("Type /exit to end this session. This session's chat history is not saved.")
    while True:
        try:
            user_text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAnima: Goodbye for now.")
            return 0
        if user_text.lower() in {"/exit", "/quit"}:
            print("Anima: Goodbye for now.")
            return 0
        if not user_text:
            continue
        if len(user_text) > MAX_INPUT_CHARS:
            print(f"Anima: Please keep each message under {MAX_INPUT_CHARS} characters.")
            continue

        history.append({"role": "user", "content": user_text})
        # Keep a bounded rolling conversation; the system prompt is added separately.
        history = history[-MAX_HISTORY_MESSAGES:]
        try:
            reply = request_reply(history, api_key, endpoint, model)
        except RuntimeError as exc:
            history.pop()  # don't keep a user message whose request failed
            print(f"Anima: I couldn't get a reply. {exc}")
            continue
        history.append({"role": "assistant", "content": reply})
        history = history[-MAX_HISTORY_MESSAGES:]
        print(f"\nAnima: {reply}")


if __name__ == "__main__":
    raise SystemExit(main())
