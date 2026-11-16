"""Refresh official FTC discovery and monitor reviewed sources. No personal data."""
import argparse, datetime as dt, hashlib, html, json, pathlib, re, sys, urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data/settlements.json"
PAGE = ROOT / "money-help/settlements-and-refunds.html"
FTC = "https://www.ftc.gov/enforcement/refunds"
UA = "NFCcopSettlementFinder/1.0 (+https://yprivateai.com/get-help.html)"
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.bits=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style"): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ("script","style"): self.skip=max(0,self.skip-1)
    def handle_data(self,s):
        if not self.skip: self.bits.append(s)
def normalized(body, content_type="text/html"):
    if "pdf" in content_type or body.startswith(b"%PDF"): return body
    parser=Text(); parser.feed(body.decode("utf-8","replace"))
    return re.sub(r"\s+"," "," ".join(parser.bits)).strip().encode()
def fetch(url):
    if urlparse(url).scheme!="https": raise ValueError("HTTPS source required")
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=35) as response:
        final=urlparse(response.geturl())
        if final.scheme!="https": raise ValueError("Insecure redirect")
        return response.read(6000000),response.headers.get("Content-Type","text/html")
class FTCLinks(HTMLParser):
    def __init__(self): super().__init__(); self.current=None; self.items=[]; self.table=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="table": self.table+=1
        if tag=="a" and self.table: self.current=[a.get("href",""),[]]
    def handle_data(self,s):
        if self.current: self.current[1].append(s)
    def handle_endtag(self,tag):
        if tag=="table": self.table=max(0,self.table-1)
        if tag=="a" and self.current:
            url=urljoin(FTC,self.current[0]); title=" ".join(" ".join(self.current[1]).split())
            p=urlparse(url)
            if p.hostname in ("www.ftc.gov","ftc.gov") and p.path.startswith("/enforcement/refunds/") and title and "faq" not in p.path:
                self.items.append((url,title))
            self.current=None
def discover(body):
    parser=FTCLinks(); parser.feed(body.decode("utf-8","replace"))
    return list(dict(parser.items).items())
def render(data):
    esc=html.escape; cards=[]
    now=dt.datetime.now(dt.timezone.utc)
    for r in sorted(data["records"],key=lambda x:(0 if x.get("review_status")=="verified" else 1,x.get("deadline_at") or "9999",x["title"])):
        closed=r.get("directory_active") is False or (bool(r.get("deadline_at")) and dt.datetime.fromisoformat(r["deadline_at"])<now)
        if closed: continue
        cards.append('<article class="card"><span class="tag">'+('FTC refund program' if r["type"]=="ftc" else 'Class-action settlement')+'</span><h3>'+esc(r["title"])+'</h3><p>'+esc(r["summary"])+'</p><p><strong>Who may qualify:</strong> '+esc(r["eligibility"])+'</p><p><strong>Deadline:</strong> '+esc(r.get("deadline_label") or "Read official instructions")+'</p><a class="button secondary" data-event="external_resource_click" target="_blank" rel="noopener noreferrer" href="'+esc(r["official_url"],quote=True)+'">Open official instructions</a></article>')
    page=PAGE.read_text(encoding="utf-8")
    page=re.sub(r"<!-- LISTINGS_START -->[\s\S]*?<!-- LISTINGS_END -->",lambda m:"<!-- LISTINGS_START -->"+"\n".join(cards)+"<!-- LISTINGS_END -->",page)
    payload=json.dumps(data,ensure_ascii=True).replace("<","\\u003c")
    page=re.sub(r'(<script id="settlement-data" type="application/json">)[\s\S]*?(</script>)',lambda m:m[1]+payload+m[2],page)
    PAGE.write_text(page,encoding="utf-8")
def update(bootstrap=False, render_only=False):
    data=json.loads(DATA.read_text(encoding="utf-8")); errors=[]
    now=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if not render_only:
        for r in data["records"]:
            if r.get("discovered_from")=="ftc": continue
            try:
                body,ctype=fetch(r["source_url"]); digest=hashlib.sha256(normalized(body,ctype)).hexdigest()
                if bootstrap and not r.get("source_hash"): r["source_hash"]=digest
                elif digest!=r.get("source_hash"):
                    r["review_status"]="needs_review"; r["change_detected_at"]=now
                r["last_checked"]=now
                r.pop("check_error",None)
            except Exception as exc:
                r["check_error"]="Official source unavailable; check manually."
                errors.append(r["id"]+": "+str(exc))
        try:
            body,_=fetch(FTC); items=discover(body)
            if len(items)<5: raise ValueError("FTC page structure changed; preserving existing directory")
            seen={url for url,title in items}
            for old in data["records"]:
                if old.get("discovered_from")=="ftc": old["directory_active"]=old["official_url"] in seen
            by_url={r["official_url"]:r for r in data["records"]}
            for url,title in items:
                if url in by_url:
                    if by_url[url].get("discovered_from")=="ftc": by_url[url]["last_checked"]=now
                    continue
                slug=urlparse(url).path.rstrip("/").split("/")[-1]
                data["records"].append(dict(id="ftc-"+slug,title=title,type="ftc",summary="Official FTC refund program. Check its instructions for eligibility and whether any action is needed.",eligibility="Read the FTC program page for the affected purchases, dates, and eligibility rules.",instructions="Open the official FTC page. Follow its instructions; some programs pay automatically and others require action.",states=["ALL"],receipt_required=None,notice_id_required=None,action="instructions",official_url=url,source_url=url,discovered_from="ftc",review_status="official_listing",last_checked=now))
            data["ftc_feed_checked"]=now
        except Exception as exc: errors.append("FTC discovery: "+str(exc))
        data["generated_at"]=now
    DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); render(data)
    if errors:
        print("\n".join(errors),file=sys.stderr)
        return 1
    print("Updated",len(data["records"]),"programs")
    return 0
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--bootstrap",action="store_true");p.add_argument("--render-only",action="store_true");a=p.parse_args()
    sys.exit(update(a.bootstrap,a.render_only))
