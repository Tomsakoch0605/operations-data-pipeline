"""Local-only simulated REST endpoint for invented transaction records."""
import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def create_server(csv_path: str | Path, host: str = "127.0.0.1", port: int = 8765):
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("demo server must bind only to loopback")
    with Path(csv_path).open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/health":
                self.respond(200, {"status": "ok"})
                return
            if url.path != "/transactions":
                self.respond(404, {"error": "not found"})
                return
            try:
                params = parse_qs(url.query)
                page = int(params.get("page", ["1"])[0])
                limit = int(params.get("limit", ["25"])[0])
                if page < 1 or not 1 <= limit <= 100:
                    raise ValueError("invalid pagination")
            except ValueError:
                self.respond(400, {"error": "invalid pagination"})
                return
            start = (page - 1) * limit
            self.respond(200, {"items": records[start:start + limit],
                               "page": page, "next_page": page + 1 if start + limit < len(records) else None})

        def respond(self, code, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return  # No request payloads or identifiers in server logs.

    return ThreadingHTTPServer((host, port), Handler)
