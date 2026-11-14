#!/usr/bin/env python3
"""Re-check the state surplus links in tools/surplus-links.json.

The links were collected on 2026-11-14 from live search results for each
state's official surplus pages. Government sites move pages often, so run this
before a rebuild to see which links no longer answer. Nothing is deleted: it
only reports, so you can fix a URL in the JSON by hand.

Run from the repo root:  python tools/harvest_surplus_links.py
"""

import concurrent.futures as futures
import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS = ROOT / "tools" / "surplus-links.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()


def check(item):
    slug, url = item
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
            text = resp.read(400000).decode("utf-8", "replace").lower()
            if resp.status == 200 and ("surplus" in text or "auction" in text or "real estate" in text):
                return slug, url, "ok"
            return slug, url, "loads, but check the content"
    except Exception as exc:  # noqa: BLE001
        return slug, url, str(exc)[:80]


def main():
    data = json.loads(LINKS.read_text(encoding="utf-8"))
    items = []
    for slug, d in sorted(data.items()):
        items.append((slug, d["url"]))
        if d.get("land_url"):
            items.append((slug, d["land_url"]))
    bad = 0
    with futures.ThreadPoolExecutor(max_workers=8) as pool:
        for slug, url, status in pool.map(check, items):
            if status != "ok":
                bad += 1
                print(f"CHECK {slug}: {status}\n      {url}")
    print(f"{len(items) - bad} of {len(items)} links ok")


if __name__ == "__main__":
    main()
