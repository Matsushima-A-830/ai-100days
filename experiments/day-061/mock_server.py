#!/usr/bin/env python3
"""Tiny logging HTTP server used as a stand-in for an internal/external endpoint.

Usage: mock_server.py PORT LOGFILE
Every request (method, path, headers subset, body) is appended as one JSON
line to LOGFILE, then the server replies 200 OK.
"""
import sys
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class LoggingHandler(BaseHTTPRequestHandler):
    logfile = None

    def _handle(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        entry = {
            "ts": time.time(),
            "method": self.command,
            "path": self.path,
            "body": body,
        }
        with open(self.logfile, "a") as f:
            f.write(json.dumps(entry) + "\n")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def log_message(self, fmt, *args):
        pass  # keep stdout clean


if __name__ == "__main__":
    port = int(sys.argv[1])
    logfile = sys.argv[2]
    LoggingHandler.logfile = logfile
    open(logfile, "a").close()
    server = HTTPServer(("127.0.0.1", port), LoggingHandler)
    print(f"mock_server listening on 127.0.0.1:{port}, logging to {logfile}")
    server.serve_forever()
