"""Bounded, retrying HTTP client for a local mock API."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen
from .validation import parse_transaction


def fetch_all(base_url: str, timeout: float = 3, retries: int = 3, limit: int = 25):
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Only loopback HTTP demo APIs are supported")
    if not 0 < timeout <= 60 or not 0 <= retries <= 10:
        raise ValueError("invalid client settings")
    page = 1
    while True:
        url = base_url.rstrip("/") + "/transactions?" + urlencode({"page": page, "limit": limit})
        for attempt in range(retries + 1):
            try:
                with urlopen(url, timeout=timeout) as response:
                    body = json.load(response)
                break
            except HTTPError as exc:
                if exc.code < 500 or attempt == retries:
                    raise
            except (URLError, TimeoutError, ConnectionError):
                if attempt == retries:
                    raise
            time.sleep(min(0.1 * (2 ** attempt), 1.0))
        if not isinstance(body, dict) or not isinstance(body.get("items"), list):
            raise ValueError("unexpected API response")
        for item in body["items"]:
            yield parse_transaction(item)
        next_page = body.get("next_page")
        if next_page is None:
            return
        if type(next_page) is not int or next_page != page + 1 or page >= 10_000:
            raise ValueError("invalid pagination sequence")
        page = next_page
