#!/usr/bin/env python3
"""Validate the generated state pages: internal links, external links, JSON-LD.

Reports:
  * internal hrefs that do not resolve to a file in the repo
  * external hrefs grouped by HTTP status (403 = bot-blocked, not necessarily dead)
  * missing title / canonical / h1, and JSON-LD that does not parse
"""

import concurrent.futures as futures
import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://yprivateai.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()

PAGES = sorted(
    list((ROOT / "probate").glob("*.html"))
    + list((ROOT / "courts").glob("*.html"))
    + list((ROOT / "legal-help").glob("file-a-civil-lawsuit-*.html"))
    + list((ROOT / "public-records").glob("warrant-information-*.html"))
)


def internal_path(href):
    parsed = urlparse(href)
    path = parsed.path if parsed.netloc else href
    path = path.split("#")[0].split("?")[0]
    if not path or path == "/":
        return ROOT / "index.html"
    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return None


def check_external(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as resp:
            return url, resp.status, resp.geturl()
    except urllib.error.HTTPError as exc:
        return url, exc.code, ""
    except Exception as exc:
        return url, type(exc).__name__, ""


def main():
    problems, externals, internal_missing = [], {}, []
    for page in PAGES:
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", text, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        h1s = re.findall(r"<h1[^>]*>", text)
        if not title or not canonical or len(h1s) != 1:
            problems.append(f"{rel}: title={bool(title)} canonical={bool(canonical)} h1={len(h1s)}")
        if canonical and canonical.group(1) != f"{SITE}/{rel}":
            problems.append(f"{rel}: canonical mismatch {canonical.group(1)}")

        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
            try:
                data = json.loads(block)
            except Exception as exc:
                problems.append(f"{rel}: JSON-LD parse error: {exc}")
                continue
            types = [n.get("@type") for n in data.get("@graph", [])]
            for need in ("Article", "BreadcrumbList", "FAQPage"):
                if need not in types:
                    problems.append(f"{rel}: JSON-LD missing {need}")

        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("mailto:", "#", "tel:")):
                continue
            if href.startswith(SITE):
                dest = internal_path(href[len(SITE):])
                if dest and not (dest.exists() or (dest / "index.html").exists()):
                    internal_missing.append(f"{rel} -> {href}")
                continue
            if href.startswith(("http://", "https://")):
                externals.setdefault(href, set()).add(rel)
                continue
            dest = internal_path(href)
            if dest is not None and not (dest.exists() or (dest / "index.html").exists()):
                internal_missing.append(f"{rel} -> {href}")

    print(f"pages: {len(PAGES)}  internal missing: {len(internal_missing)}  structural problems: {len(problems)}")
    for row in sorted(set(internal_missing))[:40]:
        print("  MISSING", row)
    for row in problems[:40]:
        print("  PROBLEM", row)

    results = {}
    with futures.ThreadPoolExecutor(max_workers=12) as ex:
        jobs = [ex.submit(check_external, url) for url in externals]
        for job in futures.as_completed(jobs):
            url, status, final = job.result()
            results[url] = (status, final)

    ok = [u for u, (s, _) in results.items() if s == 200]
    blocked = [u for u, (s, _) in results.items() if s == 403]
    bad = {u: s for u, (s, _) in results.items() if s not in (200, 403)}
    print(f"\nexternal: {len(results)} unique; 200={len(ok)}; 403-bot-blocked={len(blocked)}; other={len(bad)}")
    for url, status in sorted(bad.items()):
        pages = ", ".join(sorted(externals[url])[:3])
        print(f"  {status} {url}  [{pages}]")
    if blocked:
        print("\nbot-blocked (reachable in a normal browser):")
        for url in sorted(blocked):
            print("  403", url)


if __name__ == "__main__":
    main()
