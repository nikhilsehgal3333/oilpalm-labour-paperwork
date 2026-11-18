"""Polite HTTP downloads: one User-Agent, at least 2 seconds between requests to one host, and a
retry after HTTP 429. No personal data goes into any request."""
from __future__ import annotations

import gzip
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

USER_AGENT = "oilpalm-labour-paperwork/0.1 (independent research prototype)"
MIN_GAP = 2.0
GZIP_MAGIC = bytes([0x1F, 0x8B])
_last: dict[str, float] = {}


def get(url: str, timeout: int = 90, tries: int = 3) -> tuple[bytes, str]:
    """Return (body, final_url). Raise the last error if all tries fail."""
    host = urlparse(url).netloc
    for attempt in range(tries + 1):
        wait = MIN_GAP - (time.time() - _last.get(host, 0.0))
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                if body[:2] == GZIP_MAGIC:
                    body = gzip.decompress(body)
                return body, response.geturl()
        except urllib.error.HTTPError as error:
            if error.code == 429 and attempt < tries:
                time.sleep(30)
                continue
            raise
    raise RuntimeError("unreachable")
