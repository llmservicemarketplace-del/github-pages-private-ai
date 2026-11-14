#!/usr/bin/env python3
"""Build six 50-state resource series for phrase-match landing pages.

Outputs (50 states each, 300 pages, plus 6 by-state indexes):
  research/file-insurance-complaint-{state}.html
  money-help/apply-for-snap-{state}.html
  money-help/apply-for-medicaid-{state}.html
  money-help/energy-bill-help-{state}.html
  legal-help/small-claims-court-{state}.html
  legal-help/free-legal-aid-{state}.html

Agency names, links and phone numbers are read from the directory table on
each states/{slug}.html hub (already verified), so a correction made on a hub
flows into every series on the next run. Also links the new pages from each
state hub and section index, and appends them to sitemap.xml.

Run from the repo root:  python tools/build_state_resource_pages.py
Safe to re-run: every injection is marker-guarded.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_state_pages as B  # reuse site CSS and court data
from state_resource_data import SMALL, SNAP_NAME, MEDICAID_NAME, NOT_EXPANDED, ENERGY_NAME

SITE = "https://yprivateai.com"
TODAY = "2026-11-14"
REVIEWED = "November 14, 2026"
ZEFFY = "https://www.zeffy.com/en-US/donation-form/donate-to-change-lives-23839"
esc = B.esc

EXTRA_CSS = """
.dir th{width:34%}
.state-block{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:.4rem 1.1rem 1rem;margin:1rem 0 1.5rem}
.state-block h3{margin-top:1rem}
.more-state{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.5rem;list-style:none;padding-left:0}
.more-state li{margin:0}
.more-state a{display:block;border:1px solid var(--border);border-radius:8px;padding:.55rem .75rem;text-decoration:none;background:#fff}
"""

SERIES = {
    "ins": {
        "dir": "research", "file": "file-insurance-complaint-{slug}.html",
        "index": "research/insurance-complaint-by-state.html",
        "crumb": ("Insurance claims", "/research/"),
        "short": "File an insurance complaint",
        "index_title": "File an Insurance Complaint: All 50 States",
        "index_desc": "Find your state's insurance regulator, its free complaint form, and what to send. One guide for each of the 50 states.",
        "index_intro": "Every state has an insurance regulator that takes complaints from policyholders for free. Choose your state for the agency, its complaint page, the phone number where the agency publishes one, and the steps.",
        "general": ("/research/insurance-department-complaint.html", "how an insurance department complaint works"),
    },
    "snap": {
        "dir": "money-help", "file": "apply-for-snap-{slug}.html",
        "index": "money-help/snap-by-state.html",
        "crumb": ("Bills and benefits", "/money-help/"),
        "short": "Apply for SNAP (food stamps)",
        "index_title": "Apply for SNAP (Food Stamps): All 50 States",
        "index_desc": "Find your state's SNAP application, what the program is called there, and the steps to apply. One guide for each of the 50 states.",
        "index_intro": "SNAP is a federal food program, but each state runs its own application and some states use their own name for it. Choose your state for the official application and the steps.",
        "general": ("/money-help/apply-for-snap.html", "how SNAP works"),
    },
    "medicaid": {
        "dir": "money-help", "file": "apply-for-medicaid-{slug}.html",
        "index": "money-help/medicaid-by-state.html",
        "crumb": ("Bills and benefits", "/money-help/"),
        "short": "Apply for Medicaid",
        "index_title": "Apply for Medicaid: All 50 States",
        "index_desc": "Find your state's Medicaid application, the program's local name, whether adults qualify on income, and the steps. One guide for each state.",
        "index_intro": "Medicaid is run state by state. The name, the application, and who qualifies all depend on where you live. Choose your state for the official application and the steps.",
        "general": ("/money-help/apply-for-medicaid.html", "how Medicaid works"),
    },
    "energy": {
        "dir": "money-help", "file": "energy-bill-help-{slug}.html",
        "index": "money-help/energy-bill-help-by-state.html",
        "crumb": ("Bills and benefits", "/money-help/"),
        "short": "Energy bill help (LIHEAP)",
        "index_title": "Energy Bill Help (LIHEAP): All 50 States",
        "index_desc": "Find your state's energy assistance program, where to apply, and what to do about a shutoff notice. One guide for each of the 50 states.",
        "index_intro": "LIHEAP is the federal program that helps with heating and cooling bills. Each state runs it under its own agency, and often its own name. Choose your state for where to apply.",
        "general": ("/money-help/utility-shutoff-protection.html", "utility shutoff protections"),
    },
    "small": {
        "dir": "legal-help", "file": "small-claims-court-{slug}.html",
        "index": "legal-help/small-claims-court-by-state.html",
        "crumb": ("Legal help", "/legal-help/"),
        "short": "Small claims court",
        "index_title": "Small Claims Court Limits: All 50 States",
        "index_desc": "Small claims dollar limits for all 50 states, which court hears the case, and a how-to-file guide for each state.",
        "index_intro": "Each state sets its own dollar limit for small claims and decides which court hears them. Several states raised their limits in 2024 through 2026. Choose your state for the court, the forms, and the steps.",
        "general": ("/legal-help/small-claims-court.html", "how small claims court works"),
    },
    "legal": {
        "dir": "legal-help", "file": "free-legal-aid-{slug}.html",
        "index": "legal-help/free-legal-aid-by-state.html",
        "crumb": ("Legal help", "/legal-help/"),
        "short": "Free legal aid",
        "index_title": "Free Legal Aid: All 50 States",
        "index_desc": "Find free civil legal aid in your state: the statewide legal aid site, court self-help forms, and where to turn if legal aid cannot take your case.",
        "index_intro": "Free civil legal aid is organized state by state. Choose your state for the statewide legal aid site, court self-help forms, and other places to ask.",
        "general": ("/legal-help/legal-aid-find-lawyer.html", "how to find legal aid or a lawyer"),
    },
}
ORDER = ["ins", "snap", "medicaid", "energy", "small", "legal"]


def path_for(key, slug):
    s = SERIES[key]
    return f'{s["dir"]}/{s["file"].format(slug=slug)}'


# ------------------------------------------------------------------ hub data

TOPIC_RE = {
    "small": re.compile(r"small claims|Justice Court|Magistrate Court|Conciliation|General Sessions|Justice of the Peace|magisterial", re.I),
    "snap": re.compile(r"SNAP|food|CalFresh|3Squares|one application|benefits", re.I),
    "medicaid": re.compile(r"Medicaid|Med-QUEST|health coverage|one application|benefits online|for benefits", re.I),
    "energy": re.compile(r"energy|LIHEAP|HEAP|LIEAP|fuel|HEAT\b", re.I),
    "ins": re.compile(r"insurance", re.I),
    "legal": re.compile(r"evict|civil law state|consumer complaints|self-help", re.I),
}


# Small-claims limits on the hubs that were out of date as of 2026-11-14.
HUB_FIXES = {
    "arizona": [("hears cases up to <strong>$3,500</strong>.", "hears cases up to <strong>$5,000</strong> (raised from $3,500 by a 2025 law; some court pages still show the old figure).")],
    "idaho": [("<h3>Small claims up to $5,000</h3>", "<h3>Small claims up to $15,000</h3>"),
              ("up to <strong>$5,000</strong>, are filed", "up to <strong>$15,000</strong> since July 1, 2026 (it was $5,000 before), are filed")],
    "maine": [("<h3>Small claims up to $6,000</h3>", "<h3>Small claims up to $10,000</h3>"),
              ("up to <strong>$6,000</strong>, are heard", "up to <strong>$10,000</strong> since January 1, 2026 (it was $6,000 before), are heard")],
    "kansas": [("<h3>Small claims up to $4,000</h3>", "<h3>Small claims up to $10,000</h3>"),
               ("up to <strong>$4,000</strong>, are filed", "up to <strong>$10,000</strong> (raised from $4,000 in 2024), are filed")],
    "minnesota": [("for most cases up to <strong>$15,000</strong>.", "for most cases up to <strong>$20,000</strong> ($4,000 for consumer credit claims).")],
    "west-virginia": [("civil cases up to <strong>$10,000</strong> can", "civil cases up to <strong>$20,000</strong> (raised from $10,000 in July 2025) can")],
}


def fix_hub_limits():
    fixed = 0
    for slug, reps in HUB_FIXES.items():
        path = ROOT / "states" / f"{slug}.html"
        text = path.read_text(encoding="utf-8")
        new = text
        for old, repl in reps:
            new = new.replace(old, repl)
        if new != text:
            new = new.replace('"dateModified": "2026-11-08"', f'"dateModified": "{TODAY}"')
            path.write_text(new, encoding="utf-8")
            fixed += 1
    return fixed


def load_hub(slug):
    text = (ROOT / "states" / f"{slug}.html").read_text(encoding="utf-8")
    d = {"slug": slug}
    d["name"] = re.search(r"<h1>(.*?) Help Guide", text).group(1)
    table = re.search(r'<table class="dir">(.*?)</table>', text, re.S).group(1)
    d["dir"] = {
        html.unescape(a): (html.unescape(u), html.unescape(l))
        for a, u, l in re.findall(r'<th scope="row">(.*?)</th><td><a href="(.*?)"[^>]*>(.*?)</a>', table)
    }
    box = re.search(r'<div class="box"><strong>(.*?)</strong><br>Website: <a href="(.*?)"', text, re.S)
    d["ins_agency"] = html.unescape(box.group(1))
    d["ins_site"] = html.unescape(box.group(2))
    phone = re.search(r"Consumer line: <strong>(.*?)</strong>", text)
    d["ins_phone"] = phone.group(1) if phone else ""
    how = re.search(r"<h2>How things work in .*?</h2>(.*?)<h2>", text, re.S)
    blocks = []
    if how:
        parts = re.split(r"(?=<h3>)", how.group(1).strip())
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = re.match(r"<h3>(.*?)</h3>(.*)", part, re.S)
            if m:
                blocks.append((m.group(1), m.group(2).strip()))
            else:
                blocks.append(("", part))
    d["blocks"] = blocks
    return d


def blocks_for(hub, key):
    out = []
    for title, body in hub["blocks"]:
        plain = re.sub(r"<[^>]+>", " ", title + " " + body)
        if TOPIC_RE[key].search(plain):
            out.append((title, body))
    return out


def state_block(hub, key, heading):
    blocks = blocks_for(hub, key)
    if not blocks:
        return ""
    inner = "\n".join((f"<h3>{t}</h3>\n" if t else "") + b for t, b in blocks)
    return f'<h2>{esc(heading)}</h2>\n<div class="state-block">\n{inner}\n</div>'


def short(local):
    """Program name for headings: drop a leading 'the' and any trailing parenthetical."""
    return re.sub(r"\s*\(.*\)$", "", local).replace("the ", "", 1) if local else local


def ext(url, label):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


def link_item(label, url, source):
    return f'<li>{ext(url, label)}<span class="src">{esc(source)}</span></li>'


def host(url):
    return url.split("/")[2]


def row(label, cell):
    return f'<tr><th scope="row">{esc(label)}</th><td>{cell}</td></tr>'


def fig(slug, name, caption):
    img = ROOT / "images/editorial/public-records-capitols" / f"{slug}-state-capitol.webp"
    if not img.exists():
        return ""
    credit = B.CREDITS.get(slug)
    alt = (credit and credit["alt"]) or f"State capitol building in {name}."
    credit_html = ""
    if credit:
        credit_html = esc(credit["credit"])
        if credit["source"] and credit["license_url"]:
            credit_html += (
                f' {ext(credit["source"], "Source")} &middot; {ext(credit["license_url"], credit["license"])}'
            )
    return f'''<figure class="editorial-photo">
  <img src="/images/editorial/public-records-capitols/{slug}-state-capitol.webp" alt="{esc(alt)}" width="1440" height="810" loading="lazy" decoding="async">
  <figcaption>{esc(alt)} {esc(caption)} {credit_html}</figcaption>
</figure>'''


def more_state(hub, current):
    slug, name = hub["slug"], hub["name"]
    items = [f'<li><a href="/states/{slug}.html">{esc(name)} help guide (all topics)</a></li>']
    for key in ORDER:
        if key == current:
            continue
        items.append(f'<li><a href="/{path_for(key, slug)}">{esc(SERIES[key]["short"])} in {esc(name)}</a></li>')
    items.append(f'<li><a href="/courts/find-a-courthouse-{slug}.html">Find a courthouse in {esc(name)}</a></li>')
    return f'<h2>More {esc(name)} guides</h2>\n<ul class="more-state">\n' + "\n".join(items) + "\n</ul>"


def faq_html(faq):
    return '<h2>Common questions</h2>\n' + "\n".join(f"<h3>{esc(q)}</h3>\n<p>{esc(a)}</p>" for q, a in faq)


# ------------------------------------------------------------------- shell

def shell(*, url_path, title, description, h1, crumbs, body, faq, about=None, slug=None, active=""):
    canonical = f"{SITE}/{url_path}"
    og_image = (
        f"{SITE}/images/editorial/public-records-capitols/{slug}-state-capitol.webp"
        if slug and (ROOT / "images/editorial/public-records-capitols" / f"{slug}-state-capitol.webp").exists()
        else f"{SITE}/assets/og-default.png"
    )
    article = {
        "@type": "Article",
        "@id": f"{canonical}#article",
        "url": canonical,
        "headline": h1,
        "name": title,
        "description": description,
        "inLanguage": "en-US",
        "datePublished": TODAY,
        "dateModified": TODAY,
        "isPartOf": {"@id": f"{SITE}/#website"},
        "publisher": {
            "@type": "NGO",
            "name": "The New Faith Church and Co-op, Inc.",
            "alternateName": "NFCcop",
            "url": f"{SITE}/",
        },
        "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
    }
    if about:
        article["about"] = {"@type": "State", "name": about}
    graph = [
        article,
        {
            "@type": "BreadcrumbList",
            "@id": f"{canonical}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": c[0], "item": f"{SITE}{c[1]}" if c[1] else canonical}
                for i, c in enumerate(crumbs)
            ],
        },
    ]
    if faq:
        graph.append({
            "@type": "FAQPage",
            "@id": f"{canonical}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq
            ],
        })
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    crumb_html = " &gt; ".join(
        f'<a href="{esc(c[1])}">{esc(c[0])}</a>' if c[1] else esc(c[0]) for c in crumbs
    )

    def cls(name):
        return ' class="active"' if active == name else ""

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="NFCcop">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-WHE8ZTJQG8"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'G-WHE8ZTJQG8');
gtag('config', 'AW-18465563654');
</script>
<style>{B.CSS}{EXTRA_CSS}</style>
<link rel="stylesheet" href="/css/editorial-images.css">
<script defer src="/button-conversions.js"></script>
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="/" class="brand">NFCcop<span class="brand-sub">The New Faith Church and Co-op, Inc. &middot; free public guidance</span></a>
    <div class="header-actions">
      <a href="{ZEFFY}" class="btn-donate" data-event="donate_click" data-destination="zeffy" target="_blank" rel="noopener noreferrer">Support this work</a>
      <a href="/get-help.html" style="color:#cbd5e1;text-decoration:none;font-size:.85rem">Get help</a>
    </div>
  </div>
</header>
<div class="nav-container">
  <nav class="subnav" aria-label="Main">
    <a href="/">Home</a>
    <a href="/states/">State guides</a>
    <a href="/research/"{cls("research")}>Insurance claims</a>
    <a href="/legal-help/"{cls("legal-help")}>Legal help</a>
    <a href="/money-help/"{cls("money-help")}>Bills and benefits</a>
    <a href="/health-help/">Health help</a>
    <a href="/disaster-recovery/">Disaster recovery</a>
    <a href="/get-help.html">Get help</a>
  </nav>
</div>
<main>
<div class="breadcrumbs">{crumb_html}</div>
<h1>{esc(h1)}</h1>
<p class="reviewed"><em>Last reviewed {REVIEWED}. Written by The New Faith Church and Co-op, Inc. (NFCcop), a 501(c)(3) nonprofit educational resource. General information only, not legal advice. We are not a government agency and we charge nothing for these guides.</em></p>
{body}
<aside class="nfccop-donate" aria-label="Support these free guides">
  <p><strong>This guide is free. Help keep it free.</strong></p>
  <p>These guides are written and updated by NFCcop, a small 501(c)(3) nonprofit. No paywall and no sign-up. If this page helped you, a gift keeps it online for the next family.</p>
  <p class="btns">
    <a href="{ZEFFY}" data-event="donate_click" target="_blank" rel="noopener noreferrer">Donate</a>
    <a class="alt" href="{ZEFFY}" data-event="donate_click" target="_blank" rel="noopener noreferrer">Give monthly</a>
  </p>
  <p><small>Secure giving through Zeffy. 100% of your gift goes to NFCcop. Donations are tax-deductible to the extent allowed by law.</small></p>
</aside>
<div class="disclaimer"><strong>Disclaimer:</strong> NFCcop is not a law firm, court, insurer, or government agency, and this page does not create an attorney-client relationship. Program rules, dollar limits, phone numbers, and links change. Confirm details with the agency or court before you act.</div>
</main>
<footer>
  <div class="footer-inner">
    <div class="footer-col">
      <h3>NFCcop</h3>
      <p>The New Faith Church and Co-op, Inc. is a 501(c)(3) nonprofit that publishes free, practical guides to insurance claims, benefits, courts, and disaster recovery.</p>
    </div>
    <div class="footer-col">
      <h3>Guides</h3>
      <ul>
        <li><a href="/states/">State guides</a></li>
        <li><a href="/research/">Insurance claims</a></li>
        <li><a href="/legal-help/">Legal help</a></li>
        <li><a href="/money-help/">Bills and benefits</a></li>
        <li><a href="/disaster-recovery/">Disaster recovery</a></li>
        <li><a href="/get-help.html">Get help</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Editorial rules</h3>
      <p>We link to official government offices and recognized nonprofit programs. We do not take payment for links. Agency details change, so each page says when it was last reviewed.</p>
    </div>
  </div>
  <div class="footer-bottom">&copy; 2026 The New Faith Church and Co-op, Inc. All rights reserved. General information, not legal advice.</div>
</footer>
</body>
</html>
'''


# ------------------------------------------------------------ series bodies

def ins_page(hub):
    name, slug = hub["name"], hub["slug"]
    agency, site, phone = hub["ins_agency"], hub["ins_site"], hub["ins_phone"]
    curl, clabel = hub["dir"]["File an insurance complaint"]
    full = agency
    phone_sentence = f" The consumer line is {phone}." if phone else " The agency lists its consumer help line on its website."
    faq = [
        (f"Who do I complain to about an insurance company in {name}?",
         f"The {full}. It regulates insurers that sell policies in {name} and takes complaints from policyholders."),
        (f"Does it cost anything to file an insurance complaint in {name}?",
         "No. Filing a complaint with the state insurance regulator is free, and you do not need a lawyer to do it."),
        (f"How do I file an insurance complaint in {name}?",
         f"Use the complaint page of the {full}." + phone_sentence + " Have your policy number, claim number, the company's letters, and a short dated timeline ready."),
        ("Will a complaint get my claim paid?",
         "Sometimes. The regulator can make the company answer in writing and can act when the company broke state insurance law or the policy. It cannot decide disputed facts, such as what caused the damage or what a repair should cost, and it is not your lawyer."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> In {esc(name)}, insurance complaints go to the <strong>{esc(full)}</strong>. Filing is free and you do not need a lawyer.{esc(phone_sentence)}</p>
<p>Start here: {ext(curl, clabel)}.</p>
</div>
<p>If your insurance company denied a claim, paid too little, or stopped answering, you can ask the state regulator to step in. This page covers who takes the complaint in {esc(name)}, what to send, what the regulator can and cannot do, and what to try next if the complaint does not fix the problem.</p>
{fig(slug, name, "Insurance complaints are handled by the state regulator, usually online or by mail.")}

<h2>Who takes insurance complaints in {esc(name)}</h2>
<div class="table-wrap"><table class="dir">
{row("Agency", esc(full))}
{row("Complaint page", ext(curl, clabel))}
{row("Agency website", ext(site, host(site)))}
{row("Consumer phone", f"<strong>{esc(phone)}</strong>" if phone else "Listed on the agency website")}
{row("Cost", "Free")}
{row("Covers", "Home, auto, renters, life, and most health policies sold in " + esc(name))}
</table></div>

<h2>What the regulator can and cannot do</h2>
<p><strong>It can:</strong></p>
<ul>
<li>Send your complaint to the company and require a written answer.</li>
<li>Check whether the company followed {esc(name)} insurance law and the policy language.</li>
<li>Push the company to fix a clear violation, such as ignoring a claim or missing a legal deadline.</li>
</ul>
<p><strong>It cannot:</strong></p>
<ul>
<li>Act as your lawyer or give legal advice.</li>
<li>Decide disputed facts, such as what caused the damage or how much a repair should cost.</li>
<li>Order payment when the company followed the law and the policy.</li>
</ul>
<div class="warning"><strong>A complaint does not stop the clock.</strong> Deadlines in your policy and the deadline to sue keep running while the regulator reviews your complaint. See <a href="/research/lawsuit-deadline.html">lawsuit deadlines</a>.</div>

<h2>What to gather before you file</h2>
<ul class="checklist">
<li>Your policy number and claim number</li>
<li>The company's name exactly as it appears on the policy</li>
<li>The denial letter, payment letter, or estimate you disagree with</li>
<li>Your own estimate, photos, or repair invoices</li>
<li>A short timeline: dates you reported the loss, dates of inspections, calls, and letters</li>
<li>One or two sentences on what you want: a written explanation, a reinspection, payment of a specific amount</li>
</ul>
<p>If you do not have the company's full file, you can ask for it. See <a href="/research/request-claim-file-and-policy.html">how to request your claim file and policy</a> and <a href="/research/claim-communication-log.html">keeping a claim communication log</a>.</p>

<h2>Step by step: filing an insurance complaint in {esc(name)}</h2>
<ol>
<li><strong>Ask the company first, in writing.</strong> Request the reason for the decision and the policy language it relied on. A regulator will usually ask whether you tried this.</li>
<li><strong>Open the official complaint page.</strong> Use {ext(curl, clabel)}. Do not use a paid site that offers to file for you.</li>
<li><strong>State the facts in date order.</strong> Keep it short. Say what happened, what the company did, and what you are asking for.</li>
<li><strong>Attach copies, not originals.</strong> Include the letters and estimates listed above.</li>
<li><strong>Save your confirmation or file number.</strong> You will need it to check status or add documents.</li>
<li><strong>Read the company's response.</strong> The regulator forwards your complaint and the company must answer. You normally get a copy or a summary.</li>
<li><strong>Decide your next step.</strong> If the answer does not resolve it, look at the options below.</li>
</ol>

<h2>If the complaint does not fix it</h2>
<ul>
<li><a href="/research/request-reinspection.html">Ask for a reinspection</a> or file a <a href="/research/supplemental-claim.html">supplemental claim</a> with new evidence.</li>
<li>Use the policy's <a href="/research/appraisal.html">appraisal clause</a> when the fight is about the dollar amount, or ask about <a href="/research/claim-mediation.html">mediation</a>.</li>
<li>Compare a <a href="/research/public-adjuster-vs-attorney.html">public adjuster and an attorney</a>.</li>
<li>For a smaller amount, see <a href="/{path_for("small", slug)}">small claims court in {esc(name)}</a>.</li>
<li>If you cannot afford a lawyer, see <a href="/{path_for("legal", slug)}">free legal aid in {esc(name)}</a>.</li>
</ul>

<h2>Complaints that go somewhere else</h2>
<ul>
<li><strong>Flood insurance through the National Flood Insurance Program:</strong> these policies are federal. Appeals go to FEMA, not the state. See <a href="/disaster-recovery/flood-insurance-basics.html">flood insurance basics</a>.</li>
<li><strong>Health coverage from a large employer:</strong> many employer plans are self-funded and regulated by the U.S. Department of Labor, not the state. Call the Employee Benefits Security Administration at 1-866-444-3272.</li>
<li><strong>Medicare:</strong> call 1-800-MEDICARE (1-800-633-4227). See <a href="/health-help/medicare-appeals.html">Medicare appeals</a>.</li>
<li><strong>Scams and business practices outside insurance:</strong> use the {ext(hub["dir"]["Report a consumer problem"][0], hub["dir"]["Report a consumer problem"][1])}.</li>
</ul>
{state_block(hub, "ins", f"{name} insurance rules worth knowing")}
<p>Organizing your papers first makes a complaint stronger. Our <a href="/insurance-claim-organizer.html">insurance claim organizer</a> page explains one way to keep letters, photos, and estimates together.</p>

<h2>Official links</h2>
<ul class="links">
{link_item(clabel, curl, f"{full} (official)")}
{link_item(f"{full} website", site, "Official state insurance regulator")}
{link_item("NAIC: find any state insurance department", "https://content.naic.org/state-insurance-departments", "National Association of Insurance Commissioners")}
</ul>
<p>General guide: <a href="{SERIES["ins"]["general"][0]}">{SERIES["ins"]["general"][1]}</a>. Other states: <a href="/{SERIES["ins"]["index"]}">insurance complaints by state</a>.</p>
{faq_html(faq)}
{more_state(hub, "ins")}
'''
    return dict(
        title=f"File an Insurance Complaint in {name} | NFCcop",
        description=f"How to file an insurance complaint in {name}: the {agency}, its free complaint page" + (f", phone {phone}" if phone else "") + ", what to send, and what happens next.",
        h1=f"How to File an Insurance Complaint in {name}",
        body=body, faq=faq,
    )


def snap_page(hub):
    name, slug = hub["name"], hub["slug"]
    url, label = hub["dir"]["Apply for SNAP (food)"]
    wurl, wlabel = hub["dir"]["Apply for WIC"]
    local = SNAP_NAME.get(slug)
    called = f"{name} calls SNAP <strong>{esc(local)}</strong>. It is the same federal food program." if local else f"{name} uses the federal name, SNAP. Many people still call it food stamps."
    called_plain = f"{name} calls SNAP {local}. It is the same federal food program that many people still call food stamps." if local else f"{name} uses the federal name, SNAP (Supplemental Nutrition Assistance Program). Many people still call it food stamps."
    faq = [
        (f"How do I apply for food stamps in {name}?",
         f"Apply through the state's official application: {label}. You can also apply on paper or in person at a local office. " + called_plain),
        (f"How long does SNAP take in {name}?",
         "Federal rules give the state up to 30 days to decide a complete application. If your household has very little income and money on hand, you may qualify for expedited SNAP within 7 days. Ask for it when you apply."),
        (f"What is SNAP called in {name}?", called_plain),
        ("What if my SNAP application is denied?",
         "The denial notice explains how to ask for a fair hearing. Under federal rules you generally have 90 days from the notice to request one. Legal aid can often help for free."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Apply through {ext(url, label)}. {called}</p>
<p>You can start an application with just your name, address, and signature. That sets your filing date, and benefits are counted from it.</p>
</div>
<p>SNAP puts money for groceries on an EBT card each month. The federal government pays for it and sets the main rules, but {esc(name)} takes the application, holds the interview, and decides the case. This page covers where to apply in {esc(name)}, what to have ready, how long it takes, and what to do if you are denied.</p>
{fig(slug, name, "SNAP applications are handled by the state agency and its local offices.")}

<h2>Where to apply in {esc(name)}</h2>
<div class="table-wrap"><table class="dir">
{row("Official application", ext(url, label))}
{row("Program name in " + name, esc(local) if local else "SNAP")}
{row("Cost to apply", "Free. Never pay a website to apply.")}
{row("How benefits arrive", "On an EBT card you use like a debit card at grocery stores")}
{row("WIC (pregnancy, infants, children under 5)", ext(wurl, wlabel))}
</table></div>

<h2>Who can get SNAP</h2>
<p>Eligibility is based on your household: the people who buy and prepare food together. The state looks at:</p>
<ul>
<li><strong>Income</strong> against limits that rise with household size.</li>
<li><strong>Certain expenses</strong>, such as rent, utilities, child care, and medical costs for people who are 60 or older or disabled. These can raise your benefit.</li>
<li><strong>Citizenship or immigration status</strong> of each person applying. You can apply for eligible children even if you are not eligible yourself.</li>
<li><strong>Work rules</strong> for some adults without young children. Federal work rules changed in 2025, so read what the {esc(name)} agency says applies to you.</li>
</ul>
<p>You do not have to be unemployed. Many working households qualify. The only way to know is to apply.</p>

<h2>What to have ready</h2>
<ul class="checklist">
<li>Photo ID for the person applying</li>
<li>Social Security numbers for the people applying</li>
<li>Proof of income: pay stubs, benefit letters, or a statement from an employer</li>
<li>Rent or mortgage amount and utility bills</li>
<li>Child care costs, and child support paid</li>
<li>Medical bills for household members who are 60 or older or disabled</li>
</ul>
<p>Missing a document is not a reason to wait. File first to lock in the date, then send the rest.</p>

<h2>Step by step: applying for SNAP in {esc(name)}</h2>
<ol>
<li><strong>Submit the application.</strong> Use {ext(url, label)}, or ask a local office for a paper form.</li>
<li><strong>Ask about expedited SNAP.</strong> If you have little or no income and money on hand, federal rules require a decision within 7 days.</li>
<li><strong>Do the interview.</strong> Most interviews are by phone. If you miss the call, call back right away to reschedule.</li>
<li><strong>Send the proof they ask for.</strong> The notice lists what is needed and the due date. Keep copies and proof you sent them.</li>
<li><strong>Get the decision.</strong> The state has up to 30 days from the filing date. If approved, the EBT card comes by mail with instructions to set a PIN.</li>
<li><strong>Report changes and renew on time.</strong> Your approval notice says what to report and when the certification period ends.</li>
</ol>

<h2>If you are denied or the amount looks wrong</h2>
<p>You have the right to a fair hearing. The notice explains how to ask, and federal rules generally allow 90 days. You can ask to see your case file first. See <a href="/money-help/appeal-benefits-denial.html">how to appeal a benefits denial</a> and <a href="/{path_for("legal", slug)}">free legal aid in {esc(name)}</a>.</p>

<h2>After a storm, flood, or long power outage</h2>
<ul>
<li>If food bought with SNAP was lost, you can ask for replacement benefits. Report the loss to the state agency within 10 days. See <a href="/disaster-recovery/snap-replacement-benefits.html">SNAP replacement benefits</a>.</li>
<li>After a federal disaster declaration, the state may open Disaster SNAP for households that do not normally qualify. See <a href="/money-help/disaster-snap.html">Disaster SNAP</a>.</li>
</ul>
{state_block(hub, "snap", f"How benefits work in {name}")}

<h2>Official links</h2>
<ul class="links">
{link_item(label, url, f"{name} official SNAP page ({host(url)})")}
{link_item("USDA SNAP state directory", "https://www.fns.usda.gov/snap/state-directory", "U.S. Department of Agriculture, Food and Nutrition Service")}
{link_item(wlabel, wurl, f"{name} WIC program")}
</ul>
<p>Need food today? Call or text <strong>211</strong> for food pantries near you. General guide: <a href="{SERIES["snap"]["general"][0]}">{SERIES["snap"]["general"][1]}</a>. Other states: <a href="/{SERIES["snap"]["index"]}">SNAP by state</a>.</p>
{faq_html(faq)}
{more_state(hub, "snap")}
'''
    h1 = f"How to Apply for {short(local) if local else 'SNAP'} ({'SNAP Food Stamps' if local else 'Food Stamps'}) in {name}"
    return dict(
        title=f"Apply for SNAP (Food Stamps) in {name} | NFCcop",
        description=f"How to apply for food stamps in {name}: the official SNAP application" + (f" ({short(local)})" if local else "") + ", what to have ready, the 30-day and 7-day timelines, and how to appeal a denial.",
        h1=h1, body=body, faq=faq,
    )


def medicaid_page(hub):
    name, slug = hub["name"], hub["slug"]
    url, label = hub["dir"]["Apply for Medicaid"]
    local = MEDICAID_NAME.get(slug)
    expanded = slug not in NOT_EXPANDED
    called = f"{name}'s Medicaid program is called <strong>{esc(local)}</strong>." if local else f"{name} uses the name Medicaid."
    called_plain = f"{name}'s Medicaid program is called {local}." if local else f"{name} uses the name Medicaid."
    if expanded:
        who = f'''<p><strong>{esc(name)} has adopted the Medicaid expansion.</strong> That means most adults under 65 can qualify on income alone, up to about 138% of the federal poverty level, without having a child or a disability.</p>
<p>These groups can also qualify, often at higher income levels:</p>'''
        who_plain = f"{name} has adopted the Medicaid expansion, so most adults under 65 can qualify on income alone, up to about 138% of the federal poverty level. Children, pregnant people, adults 65 and older, and people with disabilities can also qualify under their own rules."
    else:
        extra = ""
        if slug == "georgia":
            extra = " Georgia runs a limited program called Pathways to Coverage for some adults with income up to the poverty level who meet work or activity requirements."
        if slug == "wisconsin":
            extra = " Wisconsin does cover adults without children up to the poverty level through BadgerCare Plus, even though it has not adopted the full expansion."
        who = f'''<p><strong>{esc(name)} has not adopted the Medicaid expansion.</strong> Most adults without children or a disability do not qualify on low income alone.{esc(extra)}</p>
<p>If your income is too high for Medicaid here, check HealthCare.gov. People with income at or above the poverty level may get help paying for a Marketplace plan.</p>
<p>These groups can qualify for Medicaid in {esc(name)}:</p>'''
        who_plain = f"{name} has not adopted the Medicaid expansion, so most adults without children or a disability do not qualify on low income alone.{extra} Children, pregnant people, parents with very low income, adults 65 and older, and people with disabilities may qualify."
    faq = [
        (f"How do I apply for Medicaid in {name}?",
         f"Apply through the state's official page: {label}. You can also apply through HealthCare.gov, by phone, by mail, or in person. There is no enrollment period; you can apply any time of year."),
        (f"Who qualifies for Medicaid in {name}?", who_plain),
        (f"What is Medicaid called in {name}?", called_plain),
        ("How long does a Medicaid decision take?",
         "Federal rules generally give the state up to 45 days, or up to 90 days when the application depends on a disability decision. Answer requests for documents quickly so the clock keeps moving."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Apply through {ext(url, label)}. {called} You can apply any time of year. There is no open enrollment period for Medicaid.</p>
</div>
<p>Medicaid is free or low-cost health coverage paid for by the federal government and the state together. {esc(name)} sets its own income limits within federal rules and runs its own application. This page covers who qualifies in {esc(name)}, where to apply, what to have ready, and what to do if you are denied.</p>
{fig(slug, name, "Medicaid is run by the state under federal rules.")}

<h2>Where to apply in {esc(name)}</h2>
<div class="table-wrap"><table class="dir">
{row("Official application", ext(url, label))}
{row("Program name in " + name, esc(local) if local else "Medicaid")}
{row("Medicaid expansion for adults", "Adopted" if expanded else "Not adopted")}
{row("Other ways to apply", ext("https://www.healthcare.gov/medicaid-chip/", "HealthCare.gov") + ", by phone, by mail, or at a local office")}
{row("Children's coverage (CHIP)", "Call 1-877-543-7669 (1-877-KIDS-NOW)")}
{row("Cost to apply", "Free")}
</table></div>

<h2>Who qualifies in {esc(name)}</h2>
{who}
<ul>
<li><strong>Children</strong>, through Medicaid or the Children's Health Insurance Program (CHIP)</li>
<li><strong>Pregnant people</strong>, including coverage after the birth</li>
<li><strong>Parents and caretakers</strong> of minor children</li>
<li><strong>Adults 65 and older</strong> and people with disabilities, including many who get SSI</li>
<li><strong>People who need long-term care</strong> at home or in a nursing home, under separate rules</li>
</ul>
<p>A federal law passed in 2025 adds work or community-activity rules for some adults, and states are putting them in place through 2027. The {esc(name)} agency will tell you whether they apply to you.</p>

<h2>What to have ready</h2>
<ul class="checklist">
<li>Social Security numbers and birth dates for the people applying</li>
<li>Proof of income: recent pay stubs, a benefit letter, or last year's tax return</li>
<li>Proof of citizenship or immigration status for the people applying</li>
<li>Information about any health insurance you have or can get through a job</li>
<li>For age or disability cases: bank statements and information about property</li>
</ul>

<h2>Step by step: applying for Medicaid in {esc(name)}</h2>
<ol>
<li><strong>Apply.</strong> Use {ext(url, label)}. If you start at HealthCare.gov instead, it sends your information to the state when you look eligible.</li>
<li><strong>Answer requests for proof.</strong> The state often checks income electronically and only asks for papers when something does not match. Watch your mail and your online account.</li>
<li><strong>Wait for the notice.</strong> Federal rules generally allow up to 45 days, or 90 days for disability-based cases.</li>
<li><strong>Pick a plan if asked.</strong> Many states use managed care plans. If you do not choose, one is assigned.</li>
<li><strong>Ask about recent bills.</strong> Medicaid can sometimes cover care you got shortly before you applied. Ask the agency what the current look-back period is.</li>
<li><strong>Renew every year.</strong> Keep your address current. Many people lose coverage only because a renewal letter went to an old address.</li>
</ol>

<h2>If you are denied or lose coverage</h2>
<p>The notice must say why and how to ask for a fair hearing, with a deadline. Ask right away; in some cases coverage can continue while you appeal. See <a href="/money-help/appeal-benefits-denial.html">how to appeal a benefits denial</a> and <a href="/{path_for("legal", slug)}">free legal aid in {esc(name)}</a>.</p>
<p>While you wait, see <a href="/health-help/find-low-cost-care.html">finding low-cost care</a> and <a href="/health-help/hospital-financial-assistance.html">hospital financial assistance</a>.</p>
{state_block(hub, "medicaid", f"How benefits work in {name}")}

<h2>Official links</h2>
<ul class="links">
{link_item(label, url, f"{name} official Medicaid page ({host(url)})")}
{link_item("HealthCare.gov: Medicaid and CHIP", "https://www.healthcare.gov/medicaid-chip/", "U.S. Centers for Medicare and Medicaid Services")}
</ul>
<p>General guide: <a href="{SERIES["medicaid"]["general"][0]}">{SERIES["medicaid"]["general"][1]}</a>. Other states: <a href="/{SERIES["medicaid"]["index"]}">Medicaid by state</a>.</p>
{faq_html(faq)}
{more_state(hub, "medicaid")}
'''
    nm = short(local) if local else None
    return dict(
        title=f"Apply for Medicaid in {name} | NFCcop",
        description=f"How to apply for Medicaid in {name}" + (f" ({nm})" if nm else "") + ": the official application, who qualifies, what to have ready, how long it takes, and how to appeal.",
        h1=f"How to Apply for Medicaid in {name}" + (f" ({nm})" if nm else ""),
        body=body, faq=faq,
    )


def energy_page(hub):
    name, slug = hub["name"], hub["slug"]
    url, label = hub["dir"]["Get energy bill help"]
    local = ENERGY_NAME.get(slug)
    called = f"In {name}, the federal LIHEAP program is known as <strong>{esc(local)}</strong>." if local else f"{name} runs the federal Low Income Home Energy Assistance Program (LIHEAP)."
    called_plain = f"In {name}, the federal LIHEAP program is known as {local}." if local else f"{name} runs the federal Low Income Home Energy Assistance Program, known as LIHEAP."
    faq = [
        (f"How do I get help paying my electric or gas bill in {name}?",
         f"{called_plain} Start at the state's official page: {label}. You usually apply through a local agency, and funds are limited, so apply early in the season."),
        (f"What is LIHEAP called in {name}?", called_plain),
        ("Can I get help if I already have a shutoff notice?",
         "Often, yes. Most state programs have crisis assistance for households facing disconnection or running out of fuel. Tell the agency about the notice when you apply, and call the utility the same day to ask for a payment plan."),
        ("Do I have to pay energy assistance back?",
         "No. LIHEAP is a grant, usually paid straight to your utility or fuel company. It is not a loan."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> {called} Start here: {ext(url, label)}.</p>
<p>If you have a shutoff notice, call your utility today and ask for a payment plan, then apply for crisis assistance.</p>
</div>
<p>Energy assistance is a grant that helps pay a heating or cooling bill. It is usually paid straight to the utility or fuel company, and you do not pay it back. This page covers where to apply in {esc(name)}, who qualifies, what to have ready, and what else to try.</p>
{fig(slug, name, "Energy assistance is funded federally and run by the state through local agencies.")}

<h2>Where to apply in {esc(name)}</h2>
<div class="table-wrap"><table class="dir">
{row("Official program page", ext(url, label))}
{row("Program name in " + name, esc(local) if local else "LIHEAP")}
{row("Find a local office", ext("https://acf.gov/ocs/map/liheap-map-state-and-territory-contact-listing", "LIHEAP state contact listing") + ", or call the national referral line at 1-866-674-6327")}
{row("Cost to apply", "Free")}
{row("Other local help", "Call or text 211")}
</table></div>

<h2>What the program can pay for</h2>
<ul>
<li><strong>Regular bill help:</strong> a one-time payment toward heating, and in some states cooling.</li>
<li><strong>Crisis help:</strong> faster help when you have a shutoff notice, are already disconnected, or are almost out of fuel.</li>
<li><strong>Repairs:</strong> some states fix or replace an unsafe furnace or air conditioner.</li>
<li><strong>Weatherization:</strong> insulation and air sealing to lower future bills. See <a href="/money-help/apply-for-weatherization.html">applying for weatherization</a>.</li>
</ul>
<p>Each state decides which of these it offers and when. Many open for heating in the fall and close when the money runs out.</p>

<h2>Who qualifies</h2>
<p>Eligibility is based on household income and size. {esc(name)} sets its own limit inside a federal range. Households with an older adult, a person with a disability, or a young child are often served first. If you already get SNAP, SSI, or TANF, tell the agency; in many states that makes approval simpler.</p>
<p>Renters can qualify, including when heat is included in the rent in some states. Ask.</p>

<h2>What to have ready</h2>
<ul class="checklist">
<li>Photo ID for the person applying</li>
<li>Social Security numbers for household members, if the agency asks for them</li>
<li>Proof of income for everyone in the home for the period the agency names</li>
<li>Your most recent utility or fuel bill, with the account number</li>
<li>Any shutoff or disconnection notice</li>
<li>Your lease, if utilities are part of your rent</li>
</ul>

<h2>Step by step</h2>
<ol>
<li><strong>Call the utility first if you are behind.</strong> Ask for a payment plan and ask what protections apply. See <a href="/money-help/utility-payment-plans.html">utility payment plans</a>.</li>
<li><strong>Find your local agency.</strong> Start at {ext(url, label)}.</li>
<li><strong>Apply as early as you can.</strong> Funds are limited each year.</li>
<li><strong>Say so if it is an emergency.</strong> A shutoff notice, no heat, or a medical need can move you into the crisis track.</li>
<li><strong>Tell the utility you applied.</strong> Some will hold a disconnection while an application is pending.</li>
<li><strong>Keep the approval letter.</strong> It shows the amount and which bill it was paid to.</li>
</ol>

<h2>If you are facing a shutoff</h2>
<p>States limit when a utility can disconnect service, for example during extreme weather or when someone in the home has a serious medical condition. The rules differ by state and by type of utility. See <a href="/money-help/utility-shutoff-protection.html">utility shutoff protections</a> and <a href="/disaster-recovery/help-paying-heating-bills.html">help paying heating bills</a>.</p>
<p>Also ask about <a href="/money-help/water-bill-help.html">water bill help</a> and <a href="/money-help/emergency-rent-help.html">emergency rent help</a> if more than one bill is behind.</p>
{state_block(hub, "energy", f"How energy help works in {name}")}

<h2>Official links</h2>
<ul class="links">
{link_item(label, url, f"{name} official energy assistance page ({host(url)})")}
{link_item("LIHEAP state and territory contact listing", "https://acf.gov/ocs/map/liheap-map-state-and-territory-contact-listing", "U.S. Department of Health and Human Services, Administration for Children and Families")}
</ul>
<p>Other states: <a href="/{SERIES["energy"]["index"]}">energy bill help by state</a>.</p>
{faq_html(faq)}
{more_state(hub, "energy")}
'''
    nm = short(local) if local else "LIHEAP"
    return dict(
        title=f"{name} Energy Bill Help (LIHEAP) | NFCcop",
        description=f"Help paying an electric, gas, or heating bill in {name}: where to apply for {nm}, who qualifies, what to have ready, and what to do about a shutoff notice.",
        h1=f"Help Paying Your Energy Bill in {name}" + (f" ({nm})" if local else " (LIHEAP)"),
        body=body, faq=faq,
    )


def small_page(hub):
    name, slug = hub["name"], hub["slug"]
    court, limit, note = SMALL[slug]
    furl, flabel = hub["dir"]["Find court forms and self-help"]
    lurl, llabel = hub["dir"]["Find free legal aid"]
    cdata = B.STATES.get(slug, {})
    fee_url = cdata.get("links", {}).get("fees")
    court_cap = court[0].upper() + court[1:]
    faq = [
        (f"What is the small claims court limit in {name}?",
         f"The limit is {limit}. " + (note + " " if note else "") + "Limits change, so confirm the figure with the court before you file."),
        (f"Which court hears small claims in {name}?",
         f"{court_cap}. You usually file in the county where the defendant lives or where the dispute happened."),
        (f"Do I need a lawyer for small claims court in {name}?",
         "No. Small claims is built for people to represent themselves. Whether a lawyer is allowed to appear at all varies by state, so check the court's small claims page."),
        ("What if I win and the other side does not pay?",
         "The court does not collect for you. You may need to use tools such as wage garnishment or a bank levy, which have their own forms and fees."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> In {esc(name)}, small claims cases are heard in <strong>{esc(court)}</strong>. The limit is <strong>{esc(limit)}</strong>.</p>
{f"<p>{esc(note)}</p>" if note else ""}
</div>
<p>Small claims court is the simplified part of the civil court for lower-dollar disputes: an unreturned security deposit, an unpaid loan, a repair that was not done, damage to your car or property. The forms are short and you can file without a lawyer. This page covers the limit and the court in {esc(name)}, how to file, and what happens after.</p>
{fig(slug, name, "Small claims cases are filed with the local court clerk, not at the capitol.")}

<h2>{esc(name)} small claims at a glance</h2>
<div class="table-wrap"><table class="dir">
{row("Court", esc(court_cap))}
{row("Dollar limit", esc(limit))}
{row("Forms and self-help", ext(furl, flabel))}
{row("Filing fee", "Set by the court and the claim amount. Ask the clerk, and ask for the fee waiver form if you cannot afford it" + (" (" + ext(fee_url, "court fee information") + ")" if fee_url else "") + ".")}
{row("Where to file", "Usually the county where the defendant lives or where the dispute happened")}
{row("Find the courthouse", f'<a href="/courts/find-a-courthouse-{slug}.html">{esc(name)} courthouse guide</a>')}
</table></div>
<p>Dollar limits change. Several states raised theirs between 2024 and 2026. This figure was checked on {REVIEWED}; confirm it with the court before you file.</p>

<h2>Before you file</h2>
<ol>
<li><strong>Send a demand letter.</strong> Say what you are owed, why, and give a date. Many cases end here, and some courts expect it. See <a href="/legal-help/write-a-demand-letter.html">how to write a demand letter</a>.</li>
<li><strong>Check the deadline.</strong> Every type of claim has a statute of limitations. See <a href="/legal-help/civil-lawsuit-deadlines.html">civil lawsuit deadlines</a>.</li>
<li><strong>Get the defendant's legal name.</strong> For a business, that is the registered name, which may differ from the sign on the door.</li>
<li><strong>Ask whether you can collect.</strong> A judgment against someone with no income or assets may never be paid.</li>
</ol>

<h2>Step by step: filing small claims in {esc(name)}</h2>
<ol>
<li><strong>Get the forms.</strong> Start with {ext(furl, flabel)}, or ask the clerk of {esc(court)}.</li>
<li><strong>Fill in the claim.</strong> State the amount and, in a few plain sentences, why the defendant owes it.</li>
<li><strong>File and pay the fee.</strong> If you cannot afford it, ask for a waiver. See <a href="/legal-help/court-fee-waiver.html">court fee waivers</a>.</li>
<li><strong>Serve the defendant.</strong> The court tells you which methods count. You usually cannot hand over the papers yourself. See <a href="/legal-help/serve-court-papers.html">serving court papers</a>.</li>
<li><strong>Prepare your evidence.</strong> Bring the contract or receipt, photos, messages, estimates, and a one-page timeline. Bring copies for the judge and the other side.</li>
<li><strong>Go to the hearing.</strong> Arrive early. Be brief and stick to dates, amounts, and documents. See <a href="/legal-help/prepare-for-court-hearing.html">preparing for a court hearing</a>.</li>
<li><strong>Get the judgment.</strong> Ask the clerk how and when it is issued and whether either side can appeal.</li>
</ol>

<h2>If you win: collecting</h2>
<p>Winning gives you a judgment, not a check. If the other side does not pay, you use the court's collection tools. See <a href="/legal-help/collect-a-judgment.html">how to collect a judgment</a>.</p>

<h2>If you are the one being sued</h2>
<p>Do not ignore the papers. If you miss the response date or the hearing, the court can enter a default judgment for the full amount. See <a href="/legal-help/avoid-default-judgment.html">avoiding a default judgment</a> and <a href="/legal-help/sued-by-debt-collector.html">sued by a debt collector</a>.</p>

<h2>If your claim is over the limit</h2>
<p>You can usually either give up the amount over the limit and stay in small claims, or file a regular civil case. See <a href="/legal-help/file-a-civil-lawsuit-{slug}.html">filing a civil lawsuit in {esc(name)}</a>. For a dispute with an insurer, read <a href="/research/sue-your-insurance-company-pro-se.html">suing your insurance company without a lawyer</a> and consider <a href="/{path_for("ins", slug)}">an insurance complaint in {esc(name)}</a> first.</p>
{state_block(hub, "small", f"{name} details")}

<h2>Official links and free help</h2>
<ul class="links">
{link_item(flabel, furl, f"{name} court forms and self-help ({host(furl)})")}
{link_item(llabel, lurl, f"Free civil legal aid in {name}")}
</ul>
<p>General guide: <a href="{SERIES["small"]["general"][0]}">{SERIES["small"]["general"][1]}</a>. Other states: <a href="/{SERIES["small"]["index"]}">small claims limits by state</a>.</p>
{faq_html(faq)}
{more_state(hub, "small")}
'''
    short_limit = limit.split(" (")[0].split(" for individuals")[0]
    if slug == "new-york":
        short_limit = "up to $10,000"
    return dict(
        title=f"{name} Small Claims Court Limit: {short_limit} | NFCcop",
        description=f"Small claims court in {name}: the limit is {short_limit}. Which court hears the case, forms, filing steps, serving the defendant, and collecting.",
        h1=f"Small Claims Court in {name}: Limit, Court, and How to File",
        body=body, faq=faq,
    )


def legal_page(hub):
    name, slug = hub["name"], hub["slug"]
    lurl, llabel = hub["dir"]["Find free legal aid"]
    furl, flabel = hub["dir"]["Find court forms and self-help"]
    curl, clabel = hub["dir"]["Report a consumer problem"]
    faq = [
        (f"Where can I get free legal help in {name}?",
         f"Start with {llabel}. It is the main doorway to free civil legal aid in {name}. You can also use LawHelp.org or the Legal Services Corporation's locator, or call 211."),
        ("Who qualifies for free legal aid?",
         "Most programs serve people with low income, often up to about 125% of the federal poverty level and sometimes higher. Many also help adults 60 and older, veterans, and survivors of domestic violence without a strict income test."),
        ("What kinds of cases does legal aid take?",
         "Civil cases that affect basic needs: evictions and housing, public benefits, family safety, consumer debt, and disaster recovery. Legal aid does not handle criminal charges; ask the court for a public defender."),
        ("What if legal aid cannot take my case?",
         f"Use the court's self-help resources, listed here as {flabel}. Also ask about limited-scope lawyers and law school clinics, and see whether a volunteer lawyer program covers your county."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Start with {ext(lurl, llabel)}. It is the main doorway to free civil legal aid in {esc(name)}.</p>
<p>If you have a court date or a deadline, say so in the first sentence when you call or apply. It changes how fast they respond.</p>
</div>
<p>Free civil legal aid helps people who cannot afford a lawyer with problems like eviction, denied benefits, debt lawsuits, and disaster recovery. Programs cannot take every case, so it helps to know who qualifies, how to ask, and where else to turn. This page lists the main doors in {esc(name)}.</p>
{fig(slug, name, "Legal aid programs are independent nonprofits, not part of state government.")}

<h2>Where to start in {esc(name)}</h2>
<div class="table-wrap"><table class="dir">
{row("Statewide legal aid", ext(lurl, llabel))}
{row("Court forms and self-help", ext(furl, flabel))}
{row("Consumer complaints", ext(curl, clabel))}
{row("National legal aid finders", ext("https://www.lawhelp.org/", "LawHelp.org") + " and " + ext("https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help", "Legal Services Corporation"))}
{row("Local referrals by phone", "Call or text 211")}
{row("Criminal charges", "Ask the court for a public defender. Legal aid handles civil cases only.")}
</table></div>

<h2>Who qualifies</h2>
<ul>
<li><strong>Income:</strong> most programs serve households up to about 125% of the federal poverty level, and some go higher for certain cases.</li>
<li><strong>Older adults:</strong> many programs help people 60 and older without a strict income test.</li>
<li><strong>Veterans, survivors of domestic violence, and disaster survivors:</strong> often served through dedicated projects.</li>
<li><strong>Case type:</strong> the problem has to be one the program handles, and it has to have staff available.</li>
</ul>
<p>Being turned down does not mean you have no case. It usually means the program is out of capacity or the case type is outside its grant.</p>

<h2>What legal aid usually handles</h2>
<ul>
<li>Eviction, unsafe housing, and foreclosure. See <a href="/legal-help/eviction-notice.html">eviction notices</a>.</li>
<li>SNAP, Medicaid, SSI, and unemployment denials. See <a href="/money-help/appeal-benefits-denial.html">appealing a benefits denial</a>.</li>
<li>Debt collection lawsuits and garnishment. See <a href="/legal-help/sued-by-debt-collector.html">sued by a debt collector</a>.</li>
<li>Protective orders and family safety.</li>
<li>FEMA appeals, title problems, and contractor fraud after a disaster. See <a href="/disaster-recovery/free-legal-help-after-disaster.html">free legal help after a disaster</a>.</li>
</ul>
<p>Legal aid usually does not take injury cases or other cases where a private lawyer would work for a share of the recovery.</p>

<h2>How to ask for help</h2>
<ol>
<li><strong>Apply online or by phone.</strong> Use {ext(lurl, llabel)} to find the intake line or online application for your county.</li>
<li><strong>Lead with the deadline.</strong> Give the court date, the answer due date, or the date on the notice.</li>
<li><strong>Have your papers ready.</strong> The notice or court papers, your lease or contract, and proof of income.</li>
<li><strong>Answer the screening questions.</strong> Household size, income, and who is on the other side, so they can check for conflicts.</li>
<li><strong>Ask what level of help is offered.</strong> It may be full representation, advice by phone, help with forms, or a clinic.</li>
<li><strong>If they cannot help, ask who can.</strong> Intake staff usually know the other programs in your area.</li>
</ol>

<h2>If legal aid cannot take your case</h2>
<ul>
<li><strong>Court self-help:</strong> {ext(furl, flabel)}. Also see our guide for <a href="/self-represented.html">people representing themselves</a>.</li>
<li><strong>Limited-scope lawyers:</strong> some lawyers will handle one piece, such as reviewing a document or coaching you for a hearing, for a flat fee.</li>
<li><strong>Law school clinics and volunteer lawyer programs:</strong> ask the state or county bar association.</li>
<li><strong>Small disputes:</strong> see <a href="/{path_for("small", slug)}">small claims court in {esc(name)}</a>.</li>
<li><strong>Court costs:</strong> ask for a <a href="/legal-help/court-fee-waiver.html">fee waiver</a>.</li>
<li><strong>Insurance disputes:</strong> a free <a href="/{path_for("ins", slug)}">insurance complaint in {esc(name)}</a> does not need a lawyer.</li>
</ul>
{state_block(hub, "legal", f"{name} details")}

<h2>Official links</h2>
<ul class="links">
{link_item(llabel, lurl, f"Free civil legal aid in {name} ({host(lurl)})")}
{link_item(flabel, furl, f"{name} court forms and self-help ({host(furl)})")}
{link_item("LawHelp.org", "https://www.lawhelp.org/", "Nonprofit directory of legal aid programs and self-help by state")}
{link_item("Legal Services Corporation: get legal help", "https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help", "Federally funded legal aid locator")}
</ul>
<p>General guide: <a href="{SERIES["legal"]["general"][0]}">{SERIES["legal"]["general"][1]}</a>. Other states: <a href="/{SERIES["legal"]["index"]}">free legal aid by state</a>. Related: <a href="/courts/find-a-courthouse-{slug}.html">find a courthouse in {esc(name)}</a> and <a href="/legal-help/file-a-civil-lawsuit-{slug}.html">file a civil lawsuit in {esc(name)}</a>.</p>
{faq_html(faq)}
{more_state(hub, "legal")}
'''
    return dict(
        title=f"Free Legal Aid in {name}: Where to Get Help | NFCcop",
        description=f"Free legal aid in {name}: {llabel}, court self-help forms, who qualifies, what cases legal aid takes, and where to turn if it cannot take yours.",
        h1=f"Free Legal Aid in {name}: Where to Get Help",
        body=body, faq=faq,
    )


BUILDERS = {"ins": ins_page, "snap": snap_page, "medicaid": medicaid_page, "energy": energy_page, "small": small_page, "legal": legal_page}


# ------------------------------------------------------------------ outputs

def write(rel, content):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_pages(hubs):
    paths = []
    for key in ORDER:
        s = SERIES[key]
        for hub in hubs:
            page = BUILDERS[key](hub)
            rel = path_for(key, hub["slug"])
            crumbs = [("Home", "/"), s["crumb"], (f'{s["short"]} in {hub["name"]}', "")]
            write(rel, shell(url_path=rel, crumbs=crumbs, about=hub["name"], slug=hub["slug"], active=s["dir"], **page))
            paths.append(rel)
    return paths


def build_indexes(hubs):
    paths = []
    for key in ORDER:
        s = SERIES[key]
        if key == "small":
            rows = "\n".join(
                f'<tr><td><a href="/{path_for(key, h["slug"])}">{esc(h["name"])}</a></td><td>{esc(SMALL[h["slug"]][1])}</td><td>{esc(SMALL[h["slug"]][0][0].upper() + SMALL[h["slug"]][0][1:])}</td></tr>'
                for h in hubs
            )
            listing = f'<div class="table-wrap"><table><tr><th>State</th><th>Small claims limit</th><th>Court</th></tr>\n{rows}\n</table></div>\n<p>Checked {REVIEWED}. Limits change; confirm with the court before you file.</p>'
        else:
            grid = "\n".join(f'<a href="/{path_for(key, h["slug"])}">{esc(h["name"])}</a>' for h in hubs)
            listing = f'<div class="state-grid">\n{grid}\n</div>'
        body = f'''
<p>{esc(s["index_intro"])}</p>
<h2>Choose a state</h2>
{listing}
<p>Start with the general guide if you are not sure how the process works: <a href="{s["general"][0]}">{s["general"][1]}</a>. For everything in one place for your state, see the <a href="/states/">state help guides</a>.</p>
'''
        crumbs = [("Home", "/"), s["crumb"], (s["index_title"], "")]
        write(s["index"], shell(url_path=s["index"], title=f'{s["index_title"]} | NFCcop', description=s["index_desc"],
                                h1=s["index_title"], crumbs=crumbs, body=body, faq=[], active=s["dir"]))
        paths.append(s["index"])
    return paths


def inject(rel, marker, block, before):
    """Insert block before the first occurrence of `before`; skip if marker already present."""
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    start, end = f"<!-- {marker} -->", f"<!-- /{marker} -->"
    wrapped = f"{start}\n{block}\n{end}\n"
    if start in text:
        text = re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", lambda m: wrapped, text, count=1, flags=re.S)
    elif before in text:
        text = text.replace(before, wrapped + before, 1)
    else:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def inject_links(hubs):
    done = []
    # 1. each state hub: links to its six new pages
    for hub in hubs:
        slug, name = hub["slug"], hub["name"]
        items = "".join(f'<li><a href="/{path_for(k, slug)}">{esc(SERIES[k]["short"])} in {esc(name)}</a></li>' for k in ORDER)
        block = f"<h2>{esc(name)} step-by-step guides</h2>\n<ul>{items}</ul>"
        if inject(f"states/{slug}.html", "state-resource-links", block, '<section id="reader-questions"'):
            done.append(f"states/{slug}.html")
    # 2. section indexes and the general guides: one line to the by-state index
    targets = [
        ("research/index.html", ["ins"], "<h2>Topics</h2>"),
        ("money-help/index.html", ["snap", "medicaid", "energy"], '<h2 id="bills">'),
        ("legal-help/index.html", ["small", "legal"], '<h2 id="self-help-guides">'),
        ("states/index.html", ORDER, "<h2"),
    ]
    for rel, keys, before in targets:
        items = "".join(f'<li><a href="/{SERIES[k]["index"]}">{esc(SERIES[k]["index_title"])}</a></li>' for k in keys)
        block = f"<h2>State-by-state guides</h2>\n<ul>{items}</ul>"
        if inject(rel, "state-resource-index", block, before):
            done.append(rel)
    for key in ORDER:
        s = SERIES[key]
        rel = s["general"][0].lstrip("/")
        block = f'<p><strong>Looking for your state?</strong> See <a href="/{s["index"]}">{esc(s["index_title"])}</a>.</p>'
        if inject(rel, "state-resource-note", block, "<h2"):
            done.append(rel)
    return done


def update_sitemap(paths):
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    add = [
        f"<url><loc>{SITE}/{p}</loc><lastmod>{TODAY}</lastmod></url>"
        for p in paths if f"<loc>{SITE}/{p}</loc>" not in text
    ]
    if add:
        text = text.replace("</urlset>", "\n".join(add) + "\n</urlset>")
        sm.write_text(text, encoding="utf-8")
    return len(add)


def main():
    fix_hub_limits()
    slugs = sorted(p.stem for p in (ROOT / "states").glob("*.html") if p.stem != "index")
    hubs = [load_hub(s) for s in slugs]
    missing = [h["slug"] for h in hubs if h["slug"] not in SMALL]
    if missing:
        sys.exit(f"no small-claims data for: {missing}")
    paths = build_pages(hubs) + build_indexes(hubs)
    touched = inject_links(hubs)
    added = update_sitemap(paths)
    print(f"wrote {len(paths)} pages; linked from {len(touched)} existing pages; added {added} sitemap entries")


if __name__ == "__main__":
    main()
