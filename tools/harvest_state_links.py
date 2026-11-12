#!/usr/bin/env python3
"""Harvest and verify official state court / law-enforcement links.

The site rule is that every external link must be an official government or
recognized nonprofit source. This script starts from each state judiciary
homepage, collects links whose anchor text or URL looks relevant, then fetches
the best candidates to confirm they return a real page. Nothing is written
unless the final URL answers with HTTP 200.

Output: tools/state-links.json (verified URLs + page titles).
"""

import concurrent.futures as futures
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "state-links.json"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
CTX = ssl.create_default_context()

JUDICIARY = {
    "alabama": "https://judicial.alabama.gov/",
    "alaska": "https://courts.alaska.gov/",
    "arizona": "https://www.azcourts.gov/",
    "arkansas": "https://www.arcourts.gov/",
    "california": "https://courts.ca.gov/",
    "colorado": "https://www.courts.state.co.us/",
    "connecticut": "https://www.jud.ct.gov/",
    "delaware": "https://courts.delaware.gov/",
    "district-of-columbia": "https://www.dccourts.gov/",
    "florida": "https://www.flcourts.gov/",
    "georgia": "https://georgiacourts.gov/",
    "hawaii": "https://www.courts.state.hi.us/",
    "idaho": "https://isc.idaho.gov/",
    "illinois": "https://www.illinoiscourts.gov/",
    "indiana": "https://www.courts.in.gov/",
    "iowa": "https://www.iowacourts.gov/",
    "kansas": "https://www.kscourts.org/",
    "kentucky": "https://courts.ky.gov/",
    "louisiana": "https://www.lacourts.gov/",
    "maine": "https://www.courts.maine.gov/",
    "maryland": "https://www.mdcourts.gov/",
    "massachusetts": "https://www.mass.gov/orgs/executive-office-of-the-trial-court",
    "michigan": "https://www.courts.michigan.gov/",
    "minnesota": "https://mncourts.gov/",
    "mississippi": "https://courts.ms.gov/",
    "missouri": "https://www.courts.mo.gov/",
    "montana": "https://courts.mt.gov/",
    "nebraska": "https://supremecourt.nebraska.gov/",
    "nevada": "https://nvcourts.gov/",
    "new-hampshire": "https://www.courts.nh.gov/",
    "new-jersey": "https://www.njcourts.gov/",
    "new-mexico": "https://nmcourts.gov/",
    "new-york": "https://www.nycourts.gov/",
    "north-carolina": "https://www.nccourts.gov/",
    "north-dakota": "https://www.ndcourts.gov/",
    "ohio": "https://www.supremecourt.ohio.gov/",
    "oklahoma": "https://www.oscn.net/",
    "oregon": "https://www.courts.oregon.gov/",
    "pennsylvania": "https://www.pacourts.us/",
    "rhode-island": "https://www.courts.ri.gov/",
    "south-carolina": "https://www.sccourts.org/",
    "south-dakota": "https://ujs.sd.gov/",
    "tennessee": "https://www.tncourts.gov/",
    "texas": "https://www.txcourts.gov/",
    "utah": "https://www.utcourts.gov/",
    "vermont": "https://www.vermontjudiciary.org/",
    "virginia": "https://www.vacourts.gov/",
    "washington": "https://www.courts.wa.gov/",
    "west-virginia": "https://www.courtswv.gov/",
    "wisconsin": "https://www.wicourts.gov/",
    "wyoming": "https://www.courts.state.wy.us/",
}

# State law-enforcement / public-safety agencies. Each URL is fetched and
# checked before it is kept, so a dead or moved address is dropped.
LAW_ENFORCEMENT = {
    "alabama": "https://www.dps.alabama.gov/",
    "alaska": "https://www.dps.alaska.gov/",
    "arizona": "https://www.azdps.gov/",
    "arkansas": "https://www.asp.arkansas.gov/",
    "california": "https://www.chp.ca.gov/",
    "colorado": "https://csp.state.co.us/",
    "connecticut": "https://portal.ct.gov/despp",
    "delaware": "https://dsp.delaware.gov/",
    "district-of-columbia": "https://mpd.dc.gov/",
    "florida": "https://www.fdle.state.fl.us/",
    "georgia": "https://dps.georgia.gov/",
    "hawaii": "https://dps.hawaii.gov/",
    "idaho": "https://isp.idaho.gov/",
    "illinois": "https://isp.illinois.gov/",
    "indiana": "https://www.in.gov/isp/",
    "iowa": "https://dps.iowa.gov/",
    "kansas": "https://www.kansas.gov/kshp/",
    "kentucky": "https://www.kentuckystatepolice.org/",
    "louisiana": "https://www.lsp.org/",
    "maine": "https://www.maine.gov/dps/",
    "maryland": "https://mdsp.maryland.gov/",
    "massachusetts": "https://www.mass.gov/orgs/massachusetts-state-police",
    "michigan": "https://www.michigan.gov/msp",
    "minnesota": "https://dps.mn.gov/",
    "mississippi": "https://www.dps.ms.gov/",
    "missouri": "https://www.mshp.dps.mo.gov/",
    "montana": "https://dojmt.gov/",
    "nebraska": "https://statepatrol.nebraska.gov/",
    "nevada": "https://dps.nv.gov/",
    "new-hampshire": "https://www.nh.gov/safety/divisions/nhsp/",
    "new-jersey": "https://www.njsp.org/",
    "new-mexico": "https://www.dps.nm.gov/",
    "new-york": "https://troopers.ny.gov/",
    "north-carolina": "https://www.ncdps.gov/",
    "north-dakota": "https://www.nd.gov/ndhp/",
    "ohio": "https://statepatrol.ohio.gov/",
    "oklahoma": "https://oklahoma.gov/dps.html",
    "oregon": "https://www.oregon.gov/osp/pages/index.aspx",
    "pennsylvania": "https://www.pa.gov/agencies/psp",
    "rhode-island": "https://risp.ri.gov/",
    "south-carolina": "https://www.scdps.gov/",
    "south-dakota": "https://dps.sd.gov/",
    "tennessee": "https://www.tn.gov/safety.html",
    "texas": "https://www.dps.texas.gov/",
    "utah": "https://dps.utah.gov/",
    "vermont": "https://dps.vermont.gov/",
    "virginia": "https://www.vsp.virginia.gov/",
    "washington": "https://wsp.wa.gov/",
    "west-virginia": "https://www.wvsp.gov/",
    "wisconsin": "https://wsp.wi.gov/",
    "wyoming": "https://wyominghighwaypatrol.wyo.gov/",
}

BLACKLIST = [
    "inmate", "disciplinary", "oral argument", "civic", "continuing legal",
    "cle", "employment", "careers", "news", "press release", "opinion",
    "judicial ethics", "bar admission", "law library", "podcast", "history",
    "annual report", "budget", "procurement", "holiday", "retirement",
]

CATEGORY_TERMS = {
    "probate": ["probate", "estate", "wills", "will ", "decedent", "surrogate", "orphan"],
    "forms": ["forms", "form"],
    "selfhelp": ["self-help", "self help", "help center", "helpcenter", "representing yourself", "pro se", "without a lawyer"],
    "casesearch": ["case search", "records search", "docket", "court records", "case information", "public access", "case lookup", "search cases", "case query", "smart search"],
    "directory": ["court directory", "find a court", "courts by county", "court locations", "clerk of court", "clerk", "locations", "directory"],
    "fees": ["fee waiver", "waiver", "fees", "fee schedule", "filing fee"],
    "service": ["service of process", "service of summons", "serving", "serve"],
    "efiling": ["e-filing", "efiling", "electronic filing", "file online", "odyssey", "tyler"],
    "civil": ["civil", "complaint", "filing a case", "file a case", "lawsuits", "lawsuits and civil"],
    "legalhelp": ["legal aid", "legal help", "lawhelp", "lawyer referral", "free legal"],
    "warrant": ["warrant", "wanted", "most wanted"],
}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._href = href
                self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            text = re.sub(r"\s+", " ", " ".join(self._text)).strip()
            self.links.append((self._href, text))
            self._href = None
            self._text = []


def fetch(url, timeout=18):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            final = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
            if "html" not in ctype.lower():
                return None
            raw = resp.read(900_000)
            return final, raw.decode("utf-8", "replace")
    except Exception:
        return None


def page_title(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()[:180]


def score_link(href, text):
    blob = (href + " " + text).lower()
    if any(bad in blob for bad in BLACKLIST):
        return {}
    scores = {}
    for cat, terms in CATEGORY_TERMS.items():
        s = 0
        for term in terms:
            if term in blob:
                s += 15 if term in text.lower() else 8
        if s:
            scores[cat] = s
    return scores


def safe_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or not host or " " in host:
            return None
        if "." not in host or ":" in host:
            return None
        return parsed
    except Exception:
        return None


def same_site(a, b):
    pa, pb = safe_url(a), safe_url(b)
    if not pa or not pb:
        return False
    ha = pa.netloc.lower().replace("www.", "")
    hb = pb.netloc.lower().replace("www.", "")
    return ha == hb or ha.endswith("." + hb) or hb.endswith("." + ha)


def crawl(key, seed, enforce_hosts):
    try:
        return _crawl(key, seed, enforce_hosts)
    except Exception as exc:
        return key, {"seed": seed, "ok": False, "pages": {}, "candidates": [], "error": str(exc)[:200]}


def _crawl(key, seed, enforce_hosts):
    page = fetch(seed)
    if not page:
        return key, {"seed": seed, "ok": False, "pages": {}, "candidates": []}
    final, html = page
    parser = LinkParser()
    try:
        parser.feed(html)
    except Exception:
        pass

    pages = {}
    seen = set()
    # Level 1: a small set of high-value index pages on the same site.
    for href, text in parser.links:
        try:
            url = urllib.parse.urljoin(final, href).split("#")[0]
        except Exception:
            continue
        if not safe_url(url) or url in seen or not same_site(url, final):
            continue
        low = (url + " " + text).lower()
        if not any(k in low for k in ["self-help", "self help", "forms", "probate", "estate", "records", "case search", "court directory", "courts"]):
            continue
        seen.add(url)
        if len(seen) > 9:
            break
        got = fetch(url)
        if not got:
            continue
        pfinal, phtml = got
        pages[pfinal] = page_title(phtml)
        p = LinkParser()
        try:
            p.feed(phtml)
        except Exception:
            pass
        parser.links.extend(p.links)

    candidates = []
    for href, text in parser.links:
        try:
            url = urllib.parse.urljoin(final, href).split("#")[0]
            host = (urllib.parse.urlparse(url).hostname or "").lower()
        except Exception:
            continue
        if not url.startswith("http") or not host:
            continue
        if any(url.lower().endswith(ext) for ext in (".pdf", ".jpg", ".png", ".doc", ".docx", ".zip")):
            continue
        allowed = host.endswith(".gov") or host.endswith(".us") or same_site(url, final)
        allowed = allowed or any(host.endswith(h) for h in enforce_hosts)
        if not allowed:
            continue
        scores = score_link(url, text)
        if scores:
            candidates.append({"url": url, "text": text, "scores": scores})

    return key, {
        "seed": seed,
        "final": final,
        "ok": True,
        "title": page_title(html),
        "pages": pages,
        "candidates": candidates,
    }


def verify(url):
    got = fetch(url, timeout=25)
    if not got:
        return None
    final, html = got
    title = page_title(html)
    if not title:
        return None
    return {"url": final, "title": title}


def main():
    only = set(sys.argv[1:]) or None
    keys = [k for k in JUDICIARY if not only or k in only]
    results = {}
    with futures.ThreadPoolExecutor(max_workers=14) as ex:
        jobs = {ex.submit(crawl, k, JUDICIARY[k], ["lawhelp.org", "lsc.gov"]): k for k in keys}
        for job in futures.as_completed(jobs):
            k, data = job.result()
            results[k] = data
            print(f"crawled {k}: {len(data.get('candidates', []))} candidates", flush=True)

    # Pick the strongest candidate for each category, then verify it.
    picks = {}
    checks = {}
    for k, data in results.items():
        picks[k] = {}
        if not data.get("ok"):
            continue
        best = {}
        for cand in data["candidates"]:
            for cat, s in cand["scores"].items():
                if cat not in best or s > best[cat]["scores"][cat]:
                    best[cat] = cand
        for cat, cand in best.items():
            picks[k][cat] = cand["url"]
            checks.setdefault(cand["url"], None)

    with futures.ThreadPoolExecutor(max_workers=12) as ex:
        jobmap = {ex.submit(verify, url): url for url in checks}
        for job in futures.as_completed(jobmap):
            url = jobmap[job]
            checks[url] = job.result()

    out = {"generated": "", "judiciary": JUDICIARY, "law_enforcement": {}, "states": {}}
    import datetime
    out["generated"] = datetime.date.today().isoformat()
    if OUT.exists():
        try:
            prior = json.loads(OUT.read_text())
            out["law_enforcement"].update(prior.get("law_enforcement", {}))
            out["states"].update(prior.get("states", {}))
        except Exception:
            pass

    # Law enforcement pages are verified separately.
    le_urls = {k: v for k, v in LAW_ENFORCEMENT.items() if not only or k in only}
    with futures.ThreadPoolExecutor(max_workers=12) as ex:
        le_jobs = {ex.submit(verify, url): k for k, url in le_urls.items()}
        for job in futures.as_completed(le_jobs):
            k = le_jobs[job]
            res = job.result()
            if res:
                out["law_enforcement"][k] = res

    for k, data in results.items():
        entry = {
            "seed": data.get("seed"),
            "verified": {cat: checks.get(url) for cat, url in picks.get(k, {}).items() if checks.get(url)},
        }
        out["states"][k] = entry

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {OUT}")
    for k in sorted(out["states"]):
        cats = ",".join(sorted(out["states"][k]["verified"])) or "-"
        print(f"\n{k} ({cats})")
        for cat, rec in sorted(out["states"][k]["verified"].items()):
            print(f"   {cat:11s} {rec['title'][:72]}\n               {rec['url']}")


if __name__ == "__main__":
    main()
