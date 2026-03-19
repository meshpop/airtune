#!/usr/bin/env python3
"""
Airtune web server - serves the UI and proxies recognize requests.
Port 8000.
"""

import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

API_URL = "https://api.airtune.ai/recognize"
PORT = 8000


class AirtuneHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  [{self.address_string()}] {fmt % args}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._serve_file("index.html", "text/html; charset=utf-8")
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/recognize":
            self._proxy_recognize()
        else:
            self._send_json(404, {"error": "Not found"})

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _proxy_recognize(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"

        req = urllib.request.Request(
            API_URL,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "airtune-server/1.0",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                self._send_json(200, data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                err = json.loads(error_body)
            except Exception:
                err = {"error": error_body}
            self._send_json(e.code, err)
        except Exception as e:
            self._send_json(502, {"error": str(e)})

    def _serve_file(self, filename, content_type):
        path = Path(__file__).parent / filename
        if not path.exists():
            self._send_json(404, {"error": f"{filename} not found"})
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def main():
    server = HTTPServer(("", PORT), AirtuneHandler)
    print(f"Airtune server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
