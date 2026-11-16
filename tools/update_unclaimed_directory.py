"""Refresh only state program links published by NAUPA. No visitor data."""
import datetime as dt, html, json, pathlib, sys, urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEST=ROOT/"data/unclaimed-states.json"
SOURCE="https://unclaimed.org/search/"
class Links(HTMLParser):
    def __init__(self):super().__init__();self.current=None;self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.current=[dict(attrs).get("href",""),[]]
    def handle_data(self,text):
        if self.current:self.current[1].append(text)
    def handle_endtag(self,tag):
        if tag=="a" and self.current:
            self.links.append((self.current[0]," ".join(" ".join(self.current[1]).split())));self.current=None
def parse_links(body,old):
    parser=Links();parser.feed(body)
    known={r["name"]:r for r in old["states"]};found={}
    for url,name in parser.links:
        if name not in known or name in found:continue
        if url.startswith("http://"):url="https://"+url[7:]
        p=urlparse(url)
        if p.scheme!="https" or not p.hostname or p.username or p.password:continue
        found[name]=dict(state=known[name]["state"],name=name,url=url,source=SOURCE)
    if len(found)!=51:raise ValueError("Expected all 50 states and D.C.; keeping the last known directory")
    return sorted(found.values(),key=lambda r:r["name"])
def main():
    old=json.loads(DEST.read_text(encoding="utf-8"))
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"NFCcopDirectory/1.0 (+https://yprivateai.com/get-help.html)"})
    with urllib.request.urlopen(req,timeout=35) as response:
        if urlparse(response.geturl()).hostname not in ("unclaimed.org","www.unclaimed.org"):raise ValueError("Unexpected directory redirect")
        body=response.read(5000000).decode("utf-8","replace")
    states=parse_links(body,old)
    data=dict(source=SOURCE,checked_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),states=states)
    candidate=DEST.with_suffix(".tmp")
    candidate.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8");candidate.replace(DEST)
    print("Updated 51 state program links")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("Directory unchanged:",exc,file=sys.stderr);sys.exit(1)
