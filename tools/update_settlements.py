"""Official-first settlement monitoring. Discovery leads never count as open claims."""
from __future__ import annotations
import concurrent.futures as futures, datetime as dt, hashlib, io, ipaddress, json, pathlib, re, socket, threading, time, urllib.request, urllib.robotparser
from urllib.parse import urljoin,urlparse,urlunparse,parse_qsl,urlencode
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data/settlements.json"
PAGE=ROOT/"money-help/settlements-and-refunds.html"
SOURCES=ROOT/"data/settlement-sources.json"
QUEUE=ROOT/"data/settlement-review-queue.json"
UA="NFCcopSettlementFinder/2.0 (+https://yprivateai.com/get-help.html)"
NOW=lambda:dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
_robots={};_locks={};_last={};_guard=threading.Lock()
MONTHS={m.lower():i for i,m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"],1)}
def canonical(url):
    p=urlparse(url);return urlunparse((p.scheme.lower(),p.netloc.lower().removeprefix("www."),p.path.rstrip("/") or "/","",urlencode([(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith("utm_")]),""))
def public_url(url):
    p=urlparse(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password:raise ValueError("HTTPS public source required")
    if p.port not in (None,443):raise ValueError("Nonstandard port refused")
    for addr in socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(addr[4][0]).is_global:raise ValueError("Nonpublic source refused")
    return p
def _request(url):
    public_url(url)
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/pdf,application/xml,text/plain;q=0.9,*/*;q=0.5"})
    class SafeRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):
            public_url(newurl);return super().redirect_request(req,fp,code,msg,headers,newurl)
    with urllib.request.build_opener(SafeRedirect).open(req,timeout=18) as response:
        body=response.read(8000001)
        if len(body)>8000000:raise ValueError("Source exceeds document size limit")
        return body,response.headers.get("Content-Type",""),response.geturl()
def fetch(url):
    p=public_url(url);host=p.netloc
    with _guard:lock=_locks.setdefault(host,threading.Lock())
    with lock:
        if host not in _robots:
            _robots[host]=False # Cache failed robots checks for this run; do not hammer blocked hosts
            robot_url=p.scheme+"://"+host+"/robots.txt"
            parser=urllib.robotparser.RobotFileParser()
            try:
                body,_,_=_request(robot_url);parser.parse(body.decode("utf-8","replace").splitlines())
            except urllib.error.HTTPError as exc:
                if exc.code in (401,403):raise ValueError("Source robots access unavailable")
                if exc.code not in (404,410):raise
                parser.parse([])
            _robots[host]=parser
        parser=_robots[host]
        if parser is False:raise ValueError("Source robots check failed earlier in this run")
        if not parser.can_fetch(UA,url):raise ValueError("Source robots policy blocks this path")
        pause=max(1,float(parser.crawl_delay(UA) or parser.crawl_delay("*") or 0))
        time.sleep(max(0,pause-(time.monotonic()-_last.get(host,0))))
        _last[host]=time.monotonic()
        return _request(url)
def text_body(body,ctype=""):
    if body.startswith(b"%PDF") or "application/pdf" in ctype:
        from pypdf import PdfReader
        return " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(body)).pages)
    soup=BeautifulSoup(body,"html.parser")
    for tag in soup(["script","style","nav","header","footer","noscript"]):tag.decompose()
    return soup.get_text(" ",strip=True)
def normalized(body,ctype=""):
    return re.sub(r"\s+"," ",text_body(body,ctype)).strip().encode()
def get_date(text):
    text=text.replace(","," ")
    m=re.search(r"\b("+ "|".join(MONTHS)+r")\s+(\d{1,2})(?:st|nd|rd|th)?\s+(20\d{2})\b",text,re.I)
    if m:
        try:return dt.date(int(m[3]),MONTHS[m[1].lower()],int(m[2])).isoformat()
        except ValueError:return None
    m=re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2}|20\d{2})\b",text)
    if m:
        try:return dt.date(int(m[3])+(2000 if len(m[3])==2 else 0),int(m[1]),int(m[2])).isoformat()
        except ValueError:return None
    return None
def claim_deadline(text,expected=None):
    # Only dates explicitly bound to a claim deadline/submission instruction.
    patterns=[
      r"(?:claims? (?:filing )?deadline|deadline (?:to|for) (?:submit|file|filing|submitting)[^.]{0,35}claim[^.]{0,15})\s*[:\-–—]?\s*([\s\S]{0,55})",
      r"(?:submit|file|postmark)[^.]{0,65}claim[^.]{0,40}(?:by|before|no later than)\s*([\s\S]{0,55})",
      r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d{2})\s*(?:Claim Deadline|Deadline to Submit a Claim)"
    ]
    found=[]
    for pattern in patterns:
        for m in re.finditer(pattern,text,re.I):
            date=get_date(m[1])
            if date and (expected is None or date==expected):found.append(date)
    return max(found) if found else None
def closed_signal(text):
    intro=text.lower()
    return bool(re.search(r"(?:no longer|not currently|not) accepting (?:new )?claims|claim(?:s| filing)? (?:period|deadline) (?:has )?(?:closed|passed)|deadline to (?:submit|file).{0,35}has passed",intro))
def classify_ftc(text):
    lower=text.lower()
    if closed_signal(text):return "follow_up"
    if re.search(r"can i still apply.{0,100}yes.{0,100}(?:apply|administrator)",lower):return "new_claims"
    if re.search(r"no action is needed.{0,150}(?:refund|payment)|(?:will send|send) automatic (?:refunds|payments)|you do not have to file a claim",lower):return "automatic"
    if re.search(r"second|additional|previous|first payment|filed a valid claim|reviewing claims|no longer accepting",lower):return "follow_up"
    if re.search(r"sending (?:checks|payments|refunds)|sends (?:checks|payments)|cash (?:it|your check)|accept (?:it|your payment)",lower):return "automatic"
    return "needs_review"
def active(r):
    date=r.get("deadline_date") or (r.get("deadline_at") or "")[:10]
    return not date or date>=dt.date.today().isoformat()
def check_record(record):
    r=dict(record)
    if r.get("deadline_date") and not active(r):
        r["availability"]="closed";return r
    try:
        body,ctype,final=fetch(r["source_url"])
        norm=normalized(body,ctype);text=norm.decode("utf-8","replace")
        if len(text)<150:raise ValueError("Official page has no readable notice; manual review required")
        digest=hashlib.sha256(norm).hexdigest()
        if r.get("discovered_from")=="ftc" and not r.get("editorial_override"):
            r["availability"]=classify_ftc(text);
            if r["availability"]=="new_claims":r["availability"]="needs_review" # Contact-only intake needs editorial confirmation
            r["review_status"]="action_verified" if r["availability"]!="needs_review" else "needs_review"
            r["receipt_required"]=None;r["notice_id_required"]=None
            if r["availability"]=="follow_up":
                r["summary"]="Payment distribution, existing claims, or refund follow-up. This is not listed as an opportunity to file a new claim."
                r["eligibility"]="Program-specific recipients or previously filed claimants. Read the official instructions for payment questions."
            elif r["availability"]=="automatic":
                r["summary"]="Payments are distributed using program records. This is an automatic-payment program, not an open application."
                r["eligibility"]="Only people covered by the official program qualify; an application is not offered here."
            else:
                r["summary"]="Current application availability needs confirmation. This listing is excluded from new claims."
                r["eligibility"]="Check the official agency or administrator before taking action."
            r["instructions"]="Read the official program page for the current payment, contact, or claim instructions. Do not send a preparation worksheet as a claim."
        elif r.get("action_check_only"):
            date=claim_deadline(text,r.get("deadline_date"))
            has_claim=any(re.search(r"(?:submit|file).{0,20}claim|claim form",a.get_text(" ",strip=True),re.I) for a in BeautifulSoup(body,"html.parser").find_all("a",href=True))
            if date and has_claim and not closed_signal(text):
                r["availability"]="new_claims";r["review_status"]="action_verified";r["last_verified"]=NOW()
            else:r["availability"]="needs_review";r["review_status"]="needs_review"
        elif digest!=r.get("source_hash"):
            r["review_status"]="needs_review";r["change_detected_at"]=NOW()
        r["source_hash"]=digest
        r["last_checked"]=NOW();r["source_status"]="checked";r.pop("check_error",None)
        if r.get("deadline_date") and not active(r):r["availability"]="closed"
    except Exception as exc:
        r["source_status"]="unavailable";r["check_error"]="Official source could not be rechecked: "+str(exc)[:180]
    return r
def base_record(title,url,source):
    key=hashlib.sha256(canonical(url).encode()).hexdigest()[:16]
    return dict(id="case-"+key,title=title,type="settlement",official_url=url,source_url=url,discovered_from=source,states=["UNKNOWN"],receipt_required=None,notice_id_required=None,availability="needs_review",review_status="needs_review")
def discover_source(source):
    rows=[];now=NOW()
    body,ctype,final=fetch(source["url"]);soup=BeautifulSoup(body,"html.parser")
    if source["kind"]=="classaction":
        for a in soup.select("a.js-settlement-link[href]"):
            url=urljoin(final,a["href"]);title=a.get("data-name") or a.get_text(" ",strip=True)
            card=a.find_parent("div",class_=lambda c:c and "relative" in c and "h-100" in c)
            text=card.get_text(" ",strip=True) if card else ""
            m=re.search(r"Deadline\s+(\d{1,2}/\d{1,2}/\d{2,4})",text)
            if title and m:
                r=base_record(title,url,source["id"]);r["deadline_date"]=get_date(m[1]);rows.append(r)
    elif source["kind"]=="ftc":
        for a in soup.select("table a[href]"):
            url=urljoin(final,a["href"])
            if urlparse(url).hostname in ("www.ftc.gov","ftc.gov") and urlparse(url).path.startswith("/enforcement/refunds/"):
                r=base_record(a.get_text(" ",strip=True),url,"ftc");r["type"]="ftc";rows.append(r)
    elif source["kind"]=="cfpb":
        # Ongoing is not equivalent to accepting claims. All new entries start unverified.
        for table in soup.find_all("table")[:1]:
            for a in table.select("a[href]"):
                url=urljoin(final,a["href"])
                if urlparse(url).hostname=="www.consumerfinance.gov" and "/payments-by-case/" in url:
                    r=base_record(a.get_text(" ",strip=True),url,source["id"]);r["type"]="government";rows.append(r)
    else:
        scope=soup.find("main") or soup.find("article") or soup
        for a in scope.select("a[href]"):
            url=urljoin(final,a["href"]);p=urlparse(url);title=a.get_text(" ",strip=True)
            if not title or len(title)<8 or len(title)>190 or canonical(url)==canonical(final):continue
            if source["kind"]=="directory":
                if p.hostname!=urlparse(final).hostname or not re.search(source.get("path_pattern","settlement"),p.path):continue
            elif source["kind"]=="government":
                if not re.search(r"remission|restitution|distribution|fair.?fund|refund",title+" "+p.path,re.I):continue
            else:continue
            if p.scheme=="https":rows.append(base_record(title,url,source["id"]))
    if not rows:raise ValueError("No recognized case links; source may need parser maintenance")
    source["last_checked"]=now;source["status"]="checked";source["leads_found"]=len(rows);source.pop("error",None)
    return rows
def verify_lead(r):
    if not r.get("deadline_date") or not active(r):return r
    try:
        body,ctype,final=fetch(r["source_url"]);text=normalized(body,ctype).decode("utf-8","replace");soup=BeautifulSoup(body,"html.parser")
        has_claim=any(re.search(r"(?:submit|file).{0,20}claim|claim form",a.get_text(" ",strip=True),re.I) for a in soup.find_all("a",href=True))
        date=claim_deadline(text,r["deadline_date"])
        if not date or not has_claim or closed_signal(text):return r
        r.update(availability="new_claims",review_status="action_verified",action_check_only=True,last_checked=NOW(),last_verified=NOW(),source_status="checked",source_hash=hashlib.sha256(normalized(body,ctype)).hexdigest(),action="claim",summary="The official notice lists a claim submission route and a future claim deadline. Eligibility and document requirements must be checked in that notice.",eligibility="Read the official class definition, purchase/activity dates, exclusions, and claim instructions. A filing route does not mean every visitor qualifies.",requirements="Receipt, notice-ID, and other proof requirements have not been individually reviewed for this listing.",instructions="Open the official administrator’s website, read the complete notice, and use its accepted claim form. This directory’s preparation copy is not a substitute for that form.",deadline_label=date+" — verify the cutoff time and submission method on the official site.")
    except Exception as exc:r["verification_error"]=str(exc)[:180]
    return r
def write_json(path,data):
    tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");tmp.replace(path)
def render(data):
    import html
    esc=html.escape;cards=[];today=dt.date.today()
    for r in sorted(data["records"],key=lambda x:(x.get("deadline_date") or (x.get("deadline_at") or "9999")[:10],x["title"])):
        if r.get("availability")!="new_claims" or r.get("source_status")=="unavailable" or r.get("review_status") not in ("verified","action_verified") or not active(r):continue
        try:fresh=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(r["last_checked"].replace("Z","+00:00"))).days<7
        except (ValueError,KeyError):fresh=False
        if not fresh:continue
        cards.append('<article class="card"><span class="tag">Accepting new claims</span><h3>'+esc(r["title"])+'</h3><p>'+esc(r.get("summary","Read the official notice before applying."))+'</p><p><strong>Who may qualify:</strong> '+esc(r.get("eligibility","Read the official class definition."))+'</p><p><strong>Deadline:</strong> '+esc(r.get("deadline_label","Contact administrator; deadline not verified"))+'</p><a class="button secondary" data-event="external_resource_click" target="_blank" rel="noopener noreferrer" href="'+esc(r["official_url"],quote=True)+'">Read official claim instructions</a></article>')
    page=PAGE.read_text(encoding="utf-8")
    page=re.sub(r"<!-- LISTINGS_START -->[\s\S]*?<!-- LISTINGS_END -->",lambda m:"<!-- LISTINGS_START -->"+"\n".join(cards)+"<!-- LISTINGS_END -->",page)
    payload=json.dumps(data,ensure_ascii=True).replace("<","\\u003c")
    page=re.sub(r'(<script id="settlement-data" type="application/json">)[\s\S]*?(</script>)',lambda m:m[1]+payload+m[2],page)
    PAGE.write_text(page,encoding="utf-8")
def update(render_only=False):
    data=json.loads(DATA.read_text(encoding="utf-8"));registry=json.loads(SOURCES.read_text(encoding="utf-8"));leads=[];errors=[]
    if not render_only:
        with futures.ThreadPoolExecutor(max_workers=6) as executor:data["records"]=list(executor.map(check_record,data["records"]))
        print("Checked existing official notices:",len(data["records"]),flush=True)
        for source in registry["sources"]:
            print("Discovering:",source["id"],flush=True)
            try:leads.extend(discover_source(source))
            except Exception as exc:source["status"]="unavailable";source["error"]=str(exc)[:180];errors.append(source["id"])
        known={canonical(u) for r in data["records"] for u in [r["official_url"]]+r.get("alias_urls",[])}
        old_queue=json.loads(QUEUE.read_text(encoding="utf-8")).get("leads",[]) if QUEUE.exists() else []
        dedup={canonical(r["official_url"]):r for r in old_queue if canonical(r["official_url"]) not in known}
        for r in leads:
            key=canonical(r["official_url"])
            if key not in known:dedup[key]=r
        candidates=list(dedup.values())[:1200]
        to_check=[r for r in candidates if r.get("deadline_date") and active(r)][:250]
        print("Checking discovered claim routes:",len(to_check),flush=True)
        with futures.ThreadPoolExecutor(max_workers=6) as executor:checked=list(executor.map(verify_lead,to_check))
        accepted={canonical(r["official_url"]):r for r in checked if r.get("availability")=="new_claims"}
        data["records"].extend(accepted.values())
        queue=[r for r in candidates if canonical(r["official_url"]) not in accepted]
        write_json(QUEUE,dict(updated_at=NOW(),leads=queue))
        registry["updated_at"]=NOW();write_json(SOURCES,registry)
        data["generated_at"]=NOW();data["schema_version"]=2
        data["discovery_pending"]=len(queue)
    write_json(DATA,data);render(data)
    print("Records:",len(data["records"]),"| New-claim listings:",sum(r.get("availability")=="new_claims" for r in data["records"]),"| Sources needing attention:",", ".join(errors) or "none")
    # Source-level failures are surfaced in the UI and workflow log; keep successful refreshes.
    return 0
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--render-only",action="store_true");a=p.parse_args();raise SystemExit(update(a.render_only))
