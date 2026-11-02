"""Local web interface for Project Anima.

Run: python anima_web.py
Then open http://127.0.0.1:8000 in your browser.

Configure ANIMA_GEMINI_API_KEY in the environment before starting.
The key is read only by the Python server and is never sent to the browser.
Chat history is held in server memory for this process and is not persisted.
This prototype binds to localhost only; do not expose it publicly as-is.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from chat import (
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
    MAX_HISTORY_MESSAGES,
    MAX_INPUT_CHARS,
    request_reply,
)

HOST = "127.0.0.1"
PORT = int(os.environ.get("ANIMA_WEB_PORT", "8000"))
HTML_PATH = Path(__file__).with_name("anima_chat.html")
HISTORY: list[dict[str, str]] = []


class AnimaHandler(BaseHTTPRequestHandler):
    server_version = "ProjectAnimaLocal/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path not in ("/", "/index.html"):
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            page = HTML_PATH.read_bytes()
        except OSError:
            self._send(500, b"Missing anima_chat.html", "text/plain; charset=utf-8")
            return
        self._send(200, page, "text/html; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/chat":
            self._send(404, b'{"error":"Not found"}', "application/json")
            return
        api_key = os.environ.get("ANIMA_GEMINI_API_KEY", "").strip()
        if not api_key:
            self._json(503, {"error": "The server has no ANIMA_GEMINI_API_KEY configured. Add it to your runtime environment and restart Anima."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "Invalid request length."})
            return
        if length < 1 or length > 20000:
            self._json(413, {"error": "Request is empty or too large."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            message = payload.get("message", "")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            self._json(400, {"error": "Send a valid JSON message."})
            return
        if not isinstance(message, str) or not message.strip():
            self._json(400, {"error": "Please enter a message."})
            return
        if len(message) > MAX_INPUT_CHARS:
            self._json(413, {"error": f"Keep messages under {MAX_INPUT_CHARS} characters."})
            return

        HISTORY.append({"role": "user", "content": message.strip()})
        del HISTORY[:-MAX_HISTORY_MESSAGES]
        endpoint = os.environ.get("ANIMA_CHAT_ENDPOINT", DEFAULT_ENDPOINT).strip()
        model = os.environ.get("ANIMA_CHAT_MODEL", DEFAULT_MODEL).strip()
        if not endpoint.startswith("https://") or not model:
            HISTORY.pop()
            self._json(500, {"error": "The configured endpoint must use HTTPS and the model cannot be empty."})
            return
        try:
            reply = request_reply(HISTORY, api_key, endpoint, model)
        except RuntimeError as exc:
            HISTORY.pop()
            self._json(502, {"error": str(exc)})
            return
        HISTORY.append({"role": "assistant", "content": reply})
        del HISTORY[:-MAX_HISTORY_MESSAGES]
        self._json(200, {"reply": reply})

    def _json(self, status: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        # Keep normal request logs, but never log request bodies or secrets.
        super().log_message(fmt, *args)


def main() -> None:
    if not os.environ.get("ANIMA_GEMINI_API_KEY", "").strip():
        print("Set ANIMA_GEMINI_API_KEY in your environment before starting.")
        raise SystemExit(2)
    server = ThreadingHTTPServer((HOST, PORT), AnimaHandler)
    print(f"Anima web interface: http://{HOST}:{PORT}")
    print("Localhost only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Anima web interface.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
