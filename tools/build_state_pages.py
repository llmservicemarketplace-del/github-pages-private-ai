#!/usr/bin/env python3
"""Build the state legal and public-records expansion pages.

Outputs:
  probate/{state}.html                    (51)
  courts/find-a-courthouse-{state}.html   (51)
  legal-help/file-a-civil-lawsuit-{state}.html (51)
  public-records/warrant-information-{state}.html (51)
  probate/index.html, courts/index.html
and appends the URLs to sitemap.xml.

Every page uses the site header, analytics, conversion tracking, donation
aside and legal footer. Facts are limited to the verified dataset; no fees,
dollar thresholds or deadlines are stated as numbers.
"""

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from states_part1 import STATES as S1
from states_part2 import STATES as S2

STATES = {}
STATES.update(S1)
STATES.update(S2)

REVIEWED = "November 12, 2026"
SITE = "https://yprivateai.com"
TODAY = "2026-11-12"

# Some state case portals cover only appellate or limited courts. Do not present
# them as a probate or civil case search.
SEARCH_FLAGS = {
    "ohio": {"probate": False, "civil": False},
    "texas": {"probate": False, "civil": False},
    "virginia": {"probate": False, "civil": False},
    "delaware": {"probate": False},
    "south-carolina": {"probate": False},
    "new-mexico": {"probate": False},
}

NATIONAL = {
    "lawhelp": ("LawHelp.org: free legal aid and self-help by state", "https://www.lawhelp.org/"),
    "lsc": ("Legal Services Corporation: find civil legal aid", "https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help"),
    "localgov": ("USA.gov: find your county and local government", "https://www.usa.gov/local-governments"),
    "pacer": ("PACER: federal court records", "https://pacer.uscourts.gov/"),
    "courtlistener": ("CourtListener: free federal and state opinions", "https://www.courtlistener.com/"),
    "uscourts": ("U.S. Courts: federal court forms and rules", "https://www.uscourts.gov/forms-rules"),
    "vital": ("CDC: where to get birth, death, marriage and divorce records", "https://www.cdc.gov/nchs/w2w/index.htm"),
    "unclaimed": ("Unclaimed.org: official state unclaimed property programs", "https://unclaimed.org/"),
    "nsopw": ("National Sex Offender Public Website", "https://www.nsopw.gov/"),
    "vinelink": ("VINELink: custody status and release alerts", "https://www.vinelink.com/"),
    "ada": ("ADA.gov: disability access and accommodations", "https://www.ada.gov/"),
    "lep": ("LEP.gov: language access resources", "https://www.lep.gov/"),
}

CSS = """
:root{--primary:#1e3a8a;--primary-dark:#0f172a;--secondary:#0369a1;--accent:#b45309;--danger:#b91c1c;--surface:#fff;--background:#f8fafc;--text:#1e293b;--muted:#475569;--border:#e2e8f0;--radius:8px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.7;color:var(--text);background:var(--background);display:flex;flex-direction:column;min-height:100vh}
header{background:var(--primary-dark);color:#fff;padding:1rem 1.5rem;border-bottom:3px solid var(--secondary)}
.header-inner{max-width:1160px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}
.brand{font-weight:700;font-size:1.15rem;color:#fff;text-decoration:none;letter-spacing:.4px}
.brand-sub{display:block;font-size:.8rem;font-weight:400;color:#94a3b8}
.header-actions{display:flex;align-items:center;gap:1rem}
.btn-donate{background:#047857;color:#fff!important;font-size:.85rem;font-weight:600;padding:.45rem .9rem;border-radius:4px;text-decoration:none}
.btn-donate:hover{background:#065f46}
.nav-container{background:#0f172a;border-bottom:1px solid #334155;padding:.5rem 1rem;overflow-x:auto}
nav.subnav{max-width:1160px;margin:0 auto;display:flex;flex-wrap:wrap;gap:.4rem .85rem;font-size:.875rem}
nav.subnav a{color:#cbd5e1;text-decoration:none;padding:.35rem .6rem;border-radius:4px}
nav.subnav a:hover,nav.subnav a.active{background:#1e293b;color:#38bdf8}
main{flex:1;max-width:860px;width:100%;margin:2rem auto;padding:0 1.25rem}
.breadcrumbs{font-size:.85rem;color:var(--muted);margin-bottom:1rem}
.breadcrumbs a{color:var(--secondary)}
h1{font-size:2.1rem;line-height:1.25;color:var(--primary-dark);margin-bottom:1.1rem}
h2{font-size:1.42rem;color:var(--primary);margin:2rem 0 .75rem;border-bottom:2px solid var(--border);padding-bottom:.4rem}
h3{font-size:1.12rem;color:var(--primary-dark);margin:1.3rem 0 .5rem}
p,ul,ol{margin-bottom:1.1rem}
ul,ol{padding-left:1.5rem}
li{margin-bottom:.4rem}
a{color:var(--secondary)}
.reviewed{font-size:.95rem;color:var(--muted);border-left:4px solid var(--secondary);padding:.15rem 0 .15rem .9rem;margin-bottom:1.4rem}
.quick-answer{background:#eff6ff;border:1px solid #bfdbfe;border-left:5px solid var(--secondary);border-radius:var(--radius);padding:1.1rem 1.25rem;margin:1.4rem 0}
.quick-answer p:last-child{margin-bottom:0}
.warning{background:#fffbeb;border-left:5px solid #f59e0b;padding:1rem 1.25rem;border-radius:0 var(--radius) var(--radius) 0;margin:1.4rem 0}
.safety{background:#fef2f2;border-left:5px solid var(--danger);padding:1rem 1.25rem;border-radius:0 var(--radius) var(--radius) 0;margin:1.4rem 0}
table{width:100%;border-collapse:collapse;margin:1rem 0 1.5rem;font-size:.95rem}
th,td{border:1px solid var(--border);padding:.55rem .7rem;text-align:left;vertical-align:top}
th{background:#f1f5f9;color:var(--primary-dark)}
.table-wrap{overflow-x:auto}
.checklist{list-style:none;padding-left:0}
.checklist li{padding-left:1.7rem;position:relative}
.checklist li:before{content:"\\2610";position:absolute;left:0;color:var(--primary);font-size:1.1rem;line-height:1.3}
.links{list-style:none;padding-left:0}
.links li{padding:.6rem .8rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);margin-bottom:.6rem}
.links .src{display:block;font-size:.8rem;color:var(--muted);margin-top:.15rem}
.nfccop-donate{margin:2rem 0;padding:1.1rem 1.15rem;border:2px solid #163432;border-radius:12px;background:#f2f8f7}
.nfccop-donate p{margin-bottom:.6rem}
.nfccop-donate .btns{display:flex;flex-wrap:wrap;gap:.5rem}
.nfccop-donate .btns a{display:inline-block;padding:.55rem 1rem;border-radius:8px;background:#163432;color:#fff;font-weight:700;text-decoration:none}
.nfccop-donate .btns a.alt{background:#fff;color:#163432;border:2px solid #163432}
.nfccop-donate small{color:#4a5a59}
.disclaimer{background:#f1f5f9;border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.15rem;font-size:.88rem;color:#475569;margin:2rem 0 1rem}
.state-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.5rem;margin:1rem 0 2rem}
.state-grid a{display:block;border:1px solid var(--border);border-radius:8px;padding:.6rem .75rem;text-decoration:none;background:#fff}
footer{background:var(--primary-dark);color:#94a3b8;padding:2.2rem 1.5rem;font-size:.875rem;margin-top:auto}
.footer-inner{max-width:1160px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:2rem}
.footer-col h3{color:#f1f5f9;margin-bottom:.6rem;font-size:1rem}
.footer-col ul{list-style:none;padding-left:0}
.footer-col a{color:#94a3b8;text-decoration:none}
.footer-bottom{max-width:1160px;margin:1.8rem auto 0;padding-top:1.2rem;border-top:1px solid #334155;text-align:center;font-size:.8rem}
@media(max-width:640px){h1{font-size:1.7rem}main{padding:0 1rem}}
"""


def esc(text):
    return html.escape(text, quote=True)


def load_credits():
    path = ROOT / "images/editorial/public-records-capitols/image-rights-register.csv"
    out = {}
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            page = row.get("assigned_page", "")
            slug = Path(page).stem
            out[slug] = {
                "alt": row.get("alt_text", "").strip(),
                "credit": row.get("required_attribution", "").strip(),
                "license": row.get("license", "").strip(),
                "license_url": row.get("license_url", "").strip(),
                "source": row.get("source_page", "").strip(),
            }
    return out


CREDITS = load_credits()


def fig(slug, name, topic):
    credit = CREDITS.get(slug)
    if credit:
        alt = credit["alt"] or f"{name} State Capitol."
        cap_extra = {
            "probate": "Probate files are kept by the county probate court, not at the capitol.",
            "courts": "Court addresses change; confirm with the court before you travel.",
            "civil": "Civil case files are public in most courts, but they are kept county by county.",
            "warrant": "Warrant records are held locally by courts and law enforcement agencies.",
        }[topic]
        credit_html = esc(credit["credit"])
        if credit["source"] and credit["license_url"]:
            credit_html = (
                f'{credit_html} <a href="{esc(credit["source"])}" target="_blank" rel="noopener noreferrer">Source</a>'
                f' &middot; <a href="{esc(credit["license_url"])}" target="_blank" rel="noopener noreferrer">{esc(credit["license"])}</a>'
            )
        return f'''<figure class="editorial-photo">
  <img src="/images/editorial/public-records-capitols/{slug}-state-capitol.webp" alt="{esc(alt)}" width="1440" height="810" loading="lazy" decoding="async">
  <figcaption>{esc(alt)} {cap_extra} {credit_html}</figcaption>
</figure>'''
    return f'''<figure class="editorial-photo">
  <img src="/images/editorial/public-records-capitols/{slug}-state-capitol.webp" alt="State government building in {esc(name)}." width="1440" height="810" loading="lazy" decoding="async">
  <figcaption>Government records in {esc(name)} are kept by state and county offices.</figcaption>
</figure>'''


def link_item(label, url, source):
    return f'<li><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a><span class="src">{esc(source)}</span></li>'


def gov_link(state, key, label, source):
    url = state["links"].get(key)
    return link_item(label, url, source) if url else ""


def national(key):
    label, url = NATIONAL[key]
    return link_item(label, url, url.split("/")[2])


def shell(state, *, url_path, title, description, h1, crumbs, body, faq, topic, og_image=None):
    name = state["name"]
    canonical = f"{SITE}/{url_path}"
    og_image = og_image or f"{SITE}/images/editorial/public-records-capitols/{state['slug']}-state-capitol.webp"
    faq_json = {
        "@type": "FAQPage",
        "@id": f"{canonical}#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faq
        ],
    }
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
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
                "about": {"@type": "State", "name": name},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": c[0], "item": f"{SITE}{c[1]}" if c[1] else canonical}
                    for i, c in enumerate(crumbs)
                ],
            },
            faq_json,
        ],
    }
    crumb_html = " &gt; ".join(
        f'<a href="{esc(c[1])}">{esc(c[0])}</a>' if c[1] else esc(c[0]) for c in crumbs
    )
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
<meta property="og:image:alt" content="State capitol building in {esc(name)}">
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
<style>{CSS}</style>
<link rel="stylesheet" href="/css/editorial-images.css">
<script defer src="/button-conversions.js"></script>
<script type="application/ld+json">
{json.dumps(graph, indent=2, ensure_ascii=False)}
</script>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="/" class="brand">NFCcop<span class="brand-sub">The New Faith Church and Co-op, Inc. &middot; free public guidance</span></a>
    <div class="header-actions">
      <a href="https://www.zeffy.com/en-US/donation-form/donate-to-change-lives-23839" class="btn-donate" data-event="donate_click" data-destination="zeffy" target="_blank" rel="noopener noreferrer">Support this work</a>
      <a href="/get-help.html" style="color:#cbd5e1;text-decoration:none;font-size:.85rem">Get help</a>
    </div>
  </div>
</header>
<div class="nav-container">
  <nav class="subnav" aria-label="Main">
    <a href="/">Home</a>
    <a href="/public-records/">Public records</a>
    <a href="/probate/" class="{'active' if topic == 'probate' else ''}">Probate</a>
    <a href="/courts/" class="{'active' if topic == 'courts' else ''}">Courts</a>
    <a href="/legal-help/">Legal help</a>
    <a href="/states/">State guides</a>
    <a href="/get-help.html">Get help</a>
  </nav>
</div>
<main>
<div class="breadcrumbs">{crumb_html}</div>
<h1>{esc(h1)}</h1>
<p class="reviewed"><em>Last reviewed {REVIEWED}. Written by The New Faith Church and Co-op, Inc. (NFCcop), a 501(c)(3) nonprofit educational resource. General information only, not legal advice. We sell no legal, search, background-check, or filing services.</em></p>
{body}
<aside class="nfccop-donate" aria-label="Support these free guides">
  <p><strong>This guide is free. Help keep it free.</strong></p>
  <p>These guides are written and updated by NFCcop, a small 501(c)(3) nonprofit. No paywall and no sign-up. If this page helped you, a gift keeps it online for the next family.</p>
  <p class="btns">
    <a href="https://www.zeffy.com/en-US/donation-form/donate-to-change-lives-23839" data-event="donate_click" target="_blank" rel="noopener noreferrer">Donate</a>
    <a class="alt" href="https://www.zeffy.com/en-US/donation-form/donate-to-change-lives-23839" data-event="donate_click" target="_blank" rel="noopener noreferrer">Give monthly</a>
  </p>
  <p><small>Secure giving through Zeffy. 100% of your gift goes to NFCcop. Donations are tax-deductible to the extent allowed by law.</small></p>
</aside>
<div class="disclaimer"><strong>Disclaimer:</strong> NFCcop is not a law firm, court, or government agency, and this page does not create an attorney-client relationship. Court names, addresses, forms, fees, and procedures change. Confirm details with the court or a qualified legal-aid provider before you act.</div>
</main>
<footer>
  <div class="footer-inner">
    <div class="footer-col">
      <h3>NFCcop</h3>
      <p>The New Faith Church and Co-op, Inc. is a 501(c)(3) nonprofit that publishes free, practical guides to government records, courts, and disaster recovery. We do not sell legal services, people searches, background checks, or filing services.</p>
    </div>
    <div class="footer-col">
      <h3>Guides</h3>
      <ul>
        <li><a href="/probate/">Probate by state</a></li>
        <li><a href="/courts/">Find a courthouse</a></li>
        <li><a href="/public-records/">Public records by state</a></li>
        <li><a href="/legal-help/">Legal help</a></li>
        <li><a href="/get-help.html">Get help</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Editorial rules</h3>
      <p>We link to official government offices and recognized nonprofit legal-aid programs. We do not link to people-search, mugshot, or paid background-check sites. Records may be incomplete or out of date.</p>
    </div>
  </div>
  <div class="footer-bottom">&copy; 2026 The New Faith Church and Co-op, Inc. All rights reserved. General information, not legal advice.</div>
</footer>
</body>
</html>
'''


# ---------------------------------------------------------------- topic pages

def probate_body(s):
    name, links = s["name"], s["links"]
    slug = s["slug"]
    court = links.get("court", "")
    probate = links.get("probate", "")
    search = links.get("casesearch", "") if SEARCH_FLAGS.get(slug, {}).get("probate", True) else ""
    forms = links.get("forms", "")
    selfhelp = links.get("selfhelp", "")
    directory = links.get("directory", "")
    court_dir_item = gov_link(s, "court", f"{name} judicial branch: courts, forms, and self-help", "Official state court system")
    probate_item = gov_link(s, "probate", f"{name} probate forms and self-help", "Official court page")
    search_para = (
        f'<p>The {name} court system publishes a public case lookup for some courts: <a href="{esc(search)}" target="_blank" rel="noopener noreferrer">state court case lookup</a>. It may not include probate files, and some courts post only recent or limited dockets. Treat it as a starting point, not a complete index.</p>'
        if search else
        f'<p>We could not verify a public, statewide case-search tool for {name} probate cases. That is common: probate is a county-level record, and many courts still keep it only in paper or in a local system. The probate clerk in the county where the person lived is the reliable source.</p>'
    )
    return f'''
<p>If someone in {name} died and you need to find the estate file, start with the county, not with a search engine. Probate is a court process for sorting out what a person owned, what they owed, and who inherits. A judge or clerk supervises it. In most states, the file is held by the local court that handled the death, and only part of it ever appears online.</p>
<p>This page explains which court to call in {name}, what the records contain, how to ask for a copy, and when a small estate can skip full probate. It links only to official court and government pages and to free legal-aid programs. Some wills and probate files are available online. Many are not.</p>
{fig(slug, name, "probate")}

<h2>1. What probate is, in plain words</h2>
<p>When a person dies, their money, house, car, and other property must be collected and given to the right people. Debts and taxes must be paid first. Probate is the court-supervised way to do that. The court confirms that the will is valid, appoints someone to manage the estate, and approves the final distribution.</p>
<p>Some property avoids probate. Life insurance with a named beneficiary, retirement accounts with a beneficiary, and property held with a right of survivorship usually pass directly. A house or bank account in the deceased person's name alone often does not.</p>

<h2>2. Which court handles probate in {name}</h2>
<p>{esc(s["probate"])}</p>
<div class="quick-answer"><p><strong>Start here:</strong> find the {esc(name)} court that serves the county where the person lived at the time of death. The official state court site below lists courts, forms, and self-help contacts.</p></div>
<ul class="links">
{court_dir_item}
{probate_item}
{link_item(f"{name}: find your county government", NATIONAL["localgov"][1], "USA.gov official local government directory") if not directory else gov_link(s, "directory", f"{name} court directory and locations", "Official state court system")}
</ul>

<h2>3. Find the right county and court</h2>
<p>Probate is almost always filed where the deceased person lived, even if family members live somewhere else. Use these questions to narrow it down:</p>
<ul>
<li><strong>Where did the person live?</strong> This is usually the county of residence at death, even if they were in a hospital or care facility elsewhere.</li>
<li><strong>Where is the property?</strong> A house in another county or state can create a second, separate proceeding. Ask the clerk about "ancillary" probate.</li>
<li><strong>Was a case already opened?</strong> A will may have been filed earlier. Ask the clerk to search by the person's name and date of death, not just by case number.</li>
<li><strong>Did the person live in another state?</strong> The home-state court usually starts the case. {esc(name)} may need to recognize that appointment before local property can be sold.</li>
</ul>
<p>{esc(s["nuance"]) if s.get("nuance") else f"County lines and courthouse names can be confusing. Use the official {name} court directory and call the clerk before you mail anything."}</p>

<h2>4. Search for a probate case</h2>
{search_para}
<div class="table-wrap">
<table>
<caption style="text-align:left;padding:.4rem 0;color:#475569">What you can usually find from a desk, and what needs a call or a visit</caption>
<thead><tr><th scope="col">Record</th><th scope="col">Often online?</th><th scope="col">Where to get it</th></tr></thead>
<tbody>
<tr><td>Case index (name, case number, filing date)</td><td>Sometimes</td><td>State case search, or the probate clerk</td></tr>
<tr><td>Petition to open the estate</td><td>Sometimes</td><td>Court docket or clerk copy request</td></tr>
<tr><td>Will</td><td>Rarely</td><td>Probate clerk; a filed will is part of the case file</td></tr>
<tr><td>Letters testamentary or administration</td><td>Sometimes</td><td>Clerk issues certified copies</td></tr>
<tr><td>Inventory and appraisals</td><td>Uncommon</td><td>Case file at the courthouse</td></tr>
<tr><td>Final accounting</td><td>Uncommon</td><td>Case file; may require a copy request</td></tr>
<tr><td>Order closing the estate</td><td>Sometimes</td><td>Court docket or clerk</td></tr>
</tbody>
</table>
</div>
<p>Do not assume that a "no results" screen means no estate was opened. Indexes miss names, maiden names, and initials. A clerk can search the local docket in ways a public website cannot.</p>

<h2>5. How to request a copy of a probate record in {name}</h2>
<ol>
<li><strong>Identify the county and the court.</strong> Use the directory above. Confirm the probate court's name, which can differ from the county's general courthouse.</li>
<li><strong>Gather the identifiers.</strong> Full legal name, any other names used, date of death, approximate filing year, and the case number if you have it.</li>
<li><strong>Ask what the clerk needs.</strong> Some courts require a written request or a specific form. Some accept email; many do not. Ask about certified copies versus plain copies.</li>
<li><strong>Ask about fees before ordering.</strong> Copy and certification fees are set locally and change. Ask for the current amount and how to pay.</li>
<li><strong>Keep the receipt and the envelope.</strong> If a copy is wrong or missing pages, the receipt makes a follow-up easier.</li>
<li><strong>Request an estimate if the file is large.</strong> Clerks can usually tell you the page count or the cost of a full copy.</li>
</ol>
<div class="warning"><strong>Records are not all public.</strong> A probate file can contain medical information, account numbers, or sealed material. The clerk may deny or redact parts of a file. Ask what is available before you pay for a full copy.</div>

<h2>6. Documents you will see in a probate file</h2>
<dl>
<dt><strong>Petition</strong></dt><dd>The request that opens the estate. It names the deceased person, the heirs, and the person asking to be appointed.</dd>
<dt><strong>Will</strong></dt><dd>The deceased person's written instructions. The court decides whether it is valid. A will can be filed even when there is no property to distribute.</dd>
<dt><strong>Letters testamentary</strong></dt><dd>The court order giving the named executor authority to act. Banks and title companies usually ask for a certified copy.</dd>
<dt><strong>Letters of administration</strong></dt><dd>The same authority when there is no will, or when the named executor cannot serve. The court appoints an administrator.</dd>
<dt><strong>Inventory</strong></dt><dd>A list of what the estate owns and what it is worth, usually filed within a deadline set by local rules.</dd>
<dt><strong>Final accounting</strong></dt><dd>A summary of money received, bills paid, and what is left. Some states waive it for small or uncontested estates.</dd>
<dt><strong>Closing order</strong></dt><dd>The judge's order ending the case and confirming distribution. Ask the clerk for a certified copy if a bank or buyer needs proof.</dd>
</dl>

<h2>7. Small estates and simplified probate in {name}</h2>
<p>{esc(s["small"])}</p>
<p>Every state sets its own dollar limit, waiting period, and forms. Those rules change, and a figure you find in an old blog post may be wrong. Check the current limit on the official court site or ask the probate clerk. Do not move or sell estate property based on a number you have not confirmed.</p>
<p>Real estate often follows separate rules. A small-estate affidavit may work for a bank account but not for a house. If the home was inherited without a clear deed, legal aid can help with title problems.</p>

<h2>8. Forms, self-help, and free legal help</h2>
<ul class="links">
{court_dir_item}
{probate_item}
{gov_link(s, "forms", f"{name} court forms", "Official court forms page")}
{gov_link(s, "selfhelp", f"{name} court self-help center", "Official court self-help page")}
{gov_link(s, "fees", f"{name} court fees and fee waivers", "Official court fee page")}
{link_item("Find free legal aid in your state", NATIONAL["lawhelp"][1], "LawHelp.org, a nonprofit legal-aid directory")}
{link_item("Legal Services Corporation: find civil legal aid", NATIONAL["lsc"][1], "LSC.gov, a federal nonprofit-funding agency")}
</ul>
<p>Court self-help staff can explain forms and deadlines. They usually cannot give legal advice or tell you what to write. A legal-aid office may help with an estate if you are low-income, especially when a home or benefits are at risk.</p>

<h2>9. What to gather before searching</h2>
<ul class="checklist">
<li><strong>Full legal name</strong>, including maiden name, middle name, and any spelling used on court papers</li>
<li><strong>Approximate date of death</strong>, and the state where it happened</li>
<li><strong>County of residence</strong> at the time of death</li>
<li><strong>Possible case number</strong>, if a bank, funeral home, or relative has a letter from the court</li>
<li><strong>Name of the executor or administrator</strong>, if one was appointed</li>
</ul>
<p>Also worth having: the last known address, the names of likely heirs, and a list of property in {esc(name)}. A clerk can search faster with a date and a county than with a name alone.</p>

<h2>10. Common questions</h2>
<h3>Are all {esc(name)} wills online?</h3>
<p>No. A will that has been filed may be part of the court file, but many courts do not post wills or full probate files online. Some counties publish scanned documents; others require a visit or a copy request. Never assume a will does not exist because a website did not show it.</p>
<h3>Can I search probate records for free?</h3>
<p>Often you can search an index for free and pay only for copies. Some courts charge for online access. Fees vary by county, so ask the clerk what the search and copy will cost before you order.</p>
<h3>What if the person died in {esc(name)} but lived somewhere else?</h3>
<p>The probate case usually starts where the person lived. If they owned real estate in {esc(name)}, a second local proceeding may be needed. Ask the clerk about ancillary probate and get advice if the property is valuable.</p>
<h3>Do I need a lawyer to open an estate?</h3>
<p>Not always. Simple estates are often handled without a lawyer. A contested will, a minor heir, a business, or a house with unclear title is a good reason to talk to legal aid or a lawyer before filing.</p>

<h2>11. Related guides</h2>
<ul>
<li><a href="/public-records/{slug}.html">{esc(name)} court and public records search</a></li>
<li><a href="/courts/find-a-courthouse-{slug}.html">Find a courthouse in {esc(name)}</a></li>
<li><a href="/legal-help/small-estate-affidavit.html">Settling a small estate without full probate</a></li>
<li><a href="/legal-help/file-a-civil-lawsuit-{slug}.html">How to file a civil lawsuit in {esc(name)}</a></li>
<li><a href="/legal-help/legal-aid-find-lawyer.html">Find legal aid or a lawyer</a></li>
<li><a href="/get-help.html">Ask NFCcop for help finding the right office</a></li>
</ul>
'''


def courts_body(s):
    name = s["name"]
    slug = s["slug"]
    court_item = gov_link(s, "court", f"{name} judicial branch: official court directory", "Official state court system")
    dir_item = gov_link(s, "directory", f"{name} court locations and contact information", "Official state court directory")
    return f'''
<p>{esc(name)} has more than one kind of court, and the right building depends on what you need to file or where your case is. This page shows how to use the official directory, how the courts are organized, and what to confirm by phone before you drive to a courthouse.</p>
<p>Use the official state court directory first. County and city courts usually run their own websites, and a search engine may send you to an old address or a paid directory that has nothing to do with the court.</p>
{fig(slug, name, "courts")}

<h2>Start with the official directory</h2>
<div class="quick-answer"><p><strong>Fastest route:</strong> open the {esc(name)} judicial branch directory, choose your county, then confirm the court's address and phone number on the court's own page. If the county page is missing, call the state court administrator's office.</p></div>
<ul class="links">
{court_item}
{dir_item}
{link_item("USA.gov: find your county government", NATIONAL["localgov"][1], "Official federal local-government directory")}
</ul>

<h2>How {esc(name)}'s courts are organized</h2>
<p>{esc(s["court"])}</p>
<p>Most states use some version of these levels. The names change from state to state, so do not assume that a "circuit court" in one state does the same work as a "circuit court" in another.</p>
<div class="table-wrap">
<table>
<thead><tr><th scope="col">Court type</th><th scope="col">What it usually handles</th><th scope="col">What to ask</th></tr></thead>
<tbody>
<tr><td>Supreme court</td><td>The final state appeals and court administration</td><td>Not a filing office for most cases</td></tr>
<tr><td>Appellate court</td><td>Appeals from trial courts</td><td>Whether your deadline to appeal has passed</td></tr>
<tr><td>General trial court</td><td>Felonies, larger civil claims, some family cases</td><td>Which division and which county</td></tr>
<tr><td>Limited or district court</td><td>Smaller civil claims, misdemeanors, traffic</td><td>The dollar limit and the filing window</td></tr>
<tr><td>County court</td><td>Varies widely; may handle probate or small claims</td><td>Whether your type of case is heard there</td></tr>
<tr><td>Municipal or city court</td><td>City ordinances, traffic, some small claims</td><td>Whether the city or county has jurisdiction</td></tr>
<tr><td>Probate court</td><td>Wills, estates, guardianships</td><td>Whether the court serves your county</td></tr>
<tr><td>Family court</td><td>Divorce, custody, support, protection orders</td><td>Whether filing is central or county-based</td></tr>
<tr><td>Small-claims court</td><td>Low-dollar disputes, often without lawyers</td><td>The current dollar limit and service rules</td></tr>
</tbody>
</table>
</div>
<p>In {esc(name)}, the court that handles probate is described on our <a href="/probate/{slug}.html">{esc(name)} probate guide</a>. That page also explains which county keeps the estate file.</p>

<h2>Which court handles which case</h2>
<p>Court staff can tell you where a case is filed, but they usually cannot tell you which court is legally correct for your dispute. That is a legal question. The safest path is to check the court's own filing instructions, then confirm with the clerk. If you cannot afford a lawyer, a legal-aid office or court self-help center may review the question with you.</p>
<ul>
<li><strong>Criminal or traffic:</strong> the court listed on the citation or charging document.</li>
<li><strong>Small claims:</strong> the limited-jurisdiction court for the county, when the amount is under its limit.</li>
<li><strong>Probate:</strong> the court named in the <a href="/probate/{slug}.html">{esc(name)} probate guide</a>.</li>
<li><strong>Family:</strong> the family or general trial court for the county, often where the child or spouse lives.</li>
<li><strong>Larger civil claims:</strong> the general trial court, usually in the county where the defendant lives or the dispute happened.</li>
</ul>

<h2>How to identify the correct county</h2>
<p>People often confuse four different locations. They can point to different courthouses:</p>
<ol>
<li><strong>Where a person lives.</strong> This matters for divorce, probate, and some family cases.</li>
<li><strong>Where an event occurred.</strong> A car crash or a slip-and-fall usually points to the county where it happened.</li>
<li><strong>Where property is located.</strong> A house, land, or a lien is usually handled where the property sits.</li>
<li><strong>Where a defendant may be sued.</strong> For a consumer or contract dispute, the defendant's county is often the starting point, but the rules can allow other choices.</li>
</ol>
<p>If those four answers point to different counties, do not guess. Ask the clerk which filing the court accepts, or get brief advice from legal aid. Filing in the wrong county can cost you a filing fee and delay the case.</p>

<h2>Verify before you travel</h2>
<p>Courts move, merge, and change hours. A website address that worked last year may now be a closed satellite office. Call or check the court's own page for each item below.</p>
<div class="table-wrap">
<table>
<thead><tr><th scope="col">Item</th><th scope="col">Why it matters</th></tr></thead>
<tbody>
<tr><td>Street address</td><td>Satellite and annex buildings are easy to confuse</td></tr>
<tr><td>Phone number</td><td>State and county switchboards often route to the wrong office</td></tr>
<tr><td>Office hours</td><td>Some clerks close for lunch or close early on Fridays</td></tr>
<tr><td>Filing window</td><td>A posted closing time may not be the last time a filing is accepted</td></tr>
<tr><td>Accessibility</td><td>Ask about ramps, elevators, hearing assistance, and accessible parking</td></tr>
<tr><td>Electronic filing</td><td>Some courts require it; others accept it only for certain case types</td></tr>
<tr><td>Remote hearings</td><td>Ask whether your hearing can be by video or phone, and how to join</td></tr>
</tbody>
</table>
</div>
<div class="warning"><strong>Do not rely on a paid directory.</strong> Commercial court-locator sites often copy old addresses and add phone numbers for referral services. Use the official court site or call the state court administrator.</div>

<h2>Call the clerk and ask</h2>
<p>Keep the questions short and write down the answers, the date, and the name of the person you spoke with.</p>
<ul class="checklist">
<li>Is this the right court for my type of case?</li>
<li>Which county should the case be filed in?</li>
<li>What is the filing fee, and is there a fee waiver?</li>
<li>What forms do I need, and are they on the website?</li>
<li>Can I file in person, by mail, or online?</li>
<li>What are your hours and the last time you accept a filing?</li>
<li>Where do I park, and which entrance is accessible?</li>
<li>Do you offer interpreters or hearing assistance?</li>
<li>How do I find my case number after I file?</li>
</ul>

<h2>If you are going to court for...</h2>
<ul>
<li><a href="/probate/{slug}.html">Probate or an estate in {esc(name)}</a></li>
<li><a href="/legal-help/file-a-civil-lawsuit-{slug}.html">Filing a civil lawsuit in {esc(name)}</a></li>
<li><a href="/legal-help/small-claims-court.html">Small claims court: how it works</a></li>
<li><a href="/public-records/{slug}.html">{esc(name)} court and public records search</a></li>
<li><a href="/legal-help/serve-court-papers.html">How to serve court papers</a></li>
<li><a href="/get-help.html">Ask NFCcop for help finding the right office</a></li>
</ul>

<h2>Common questions</h2>
<h3>How do I find the right courthouse in {esc(name)}?</h3>
<p>Start with the official {esc(name)} judicial branch directory, choose the county, and confirm the address and phone number on the court's own page. If you are filing, call the clerk and describe the type of case before you travel.</p>
<h3>Do I file where I live or where the defendant lives?</h3>
<p>It depends on the case. For many civil disputes, the defendant's county or the county where the events happened is allowed. Probate usually follows the deceased person's county, and property cases often follow the property. Confirm with the clerk or legal aid.</p>
<h3>Can I file by mail or online?</h3>
<p>Often yes, but not for every case type. Ask the clerk whether your court accepts mail, e-filing, or drop-box filings, and whether an original signature is required.</p>
<h3>What if I cannot afford the filing fee?</h3>
<p>Most courts have a fee-waiver process. Ask the clerk for the waiver form and what proof of income is required. See our <a href="/legal-help/court-fee-waiver.html">court fee waiver guide</a>.</p>
'''


def civil_body(s):
    name = s["name"]
    slug = s["slug"]
    court = s["links"].get("court", "")
    civil = s["links"].get("civil", "")
    forms = s["links"].get("forms", "")
    fees = s["links"].get("fees", "")
    efiling = s["links"].get("efiling", "")
    search = s["links"].get("casesearch", "") if SEARCH_FLAGS.get(slug, {}).get("civil", True) else ""
    selfhelp = s["links"].get("selfhelp", "")
    legalhelp = s["links"].get("legalhelp", "")
    return f'''
<p>A civil lawsuit is how one person or business asks a court to settle a dispute with another. It is not a criminal case, and no one goes to jail because of it. The person who files is the plaintiff; the person being sued is the defendant.</p>
<p>This guide walks through the filing sequence in {esc(name)}: choosing the court, preparing the complaint, paying or waiving the fee, serving the defendant, and tracking the case. It is general information, not legal advice, and it does not promise any result.</p>
{fig(slug, name, "civil")}

<h2>Civil cases and criminal cases are different</h2>
<ul>
<li><strong>Criminal case:</strong> a government prosecutes a person for breaking a criminal law. The punishment can include jail, fines, or both.</li>
<li><strong>Civil case:</strong> a private party sues another private party, or sometimes a government agency, over money, property, a contract, or harm. The remedy is usually money or an order to do or stop something.</li>
</ul>
<p>The same event can lead to both. A car crash can produce a traffic charge and a civil claim for repairs or medical bills. They are separate cases with separate rules.</p>

<h2>Regular civil court and small claims</h2>
<p>Small-claims court is a simplified part of the civil court for lower-dollar disputes. The forms are shorter, the hearings are informal, and lawyers are often not required. The dollar limit and the types of cases allowed vary by state.</p>
<p>If your claim is small, read our <a href="/legal-help/small-claims-court.html">small claims guide</a> before you file a regular civil case. Filing in the wrong track can waste a fee. If your claim is large or complicated, small claims may not be available.</p>

<h2>Jurisdiction and venue, in plain language</h2>
<p><strong>Jurisdiction</strong> asks whether a court has the power to hear this kind of case and this person. <strong>Venue</strong> asks which county or district is the proper location. A court can have jurisdiction but still be the wrong venue.</p>
<p>{esc(s["civil"])}</p>
<p>For a consumer, contract, or personal-injury dispute, the answer often depends on where the defendant lives, where the agreement was made, or where the harm happened. Do not assume that you can file in your own county just because it is convenient.</p>

<h2>Step by step: filing a civil lawsuit in {esc(name)}</h2>
<ol>
<li><strong>Identify the legal claim.</strong> Write down what happened, what rule or agreement was broken, and what remedy you want. "They were unfair" is not a legal claim; "they broke a written contract and owe $X" is closer.</li>
<li><strong>Check the deadline.</strong> Statutes of limitation set how long you have. They differ by claim type. Missing the deadline can end the case, so check before you spend money on filing.</li>
<li><strong>Choose the correct court and county.</strong> Use the <a href="/courts/find-a-courthouse-{slug}.html">{esc(name)} courthouse guide</a> and confirm with the clerk.</li>
<li><strong>Prepare the complaint.</strong> Most courts publish a form or a required format. State the facts in order, identify the parties, and say what you want the court to order.</li>
<li><strong>Prepare a summons if the court requires one.</strong> The clerk usually issues or stamps it. Do not invent a court form.</li>
<li><strong>Pay the filing fee or request a waiver.</strong> Ask for the current fee and the fee-waiver form at the same time.</li>
<li><strong>File with the clerk.</strong> Keep stamped copies of everything. Ask how the court assigns the case number.</li>
<li><strong>Arrange legally valid service.</strong> The defendant must receive the complaint and summons in the way the rules allow. In most states, a party to the case cannot do this personally.</li>
<li><strong>Keep proof of service.</strong> File the affidavit or certificate with the court. Without it, the case may not move forward.</li>
<li><strong>Track deadlines and hearings.</strong> Put every date on a calendar, check the docket, and respond to motions. A missed deadline can cost you the case.</li>
</ol>

<h2>Deadlines: there is no single answer</h2>
<p>{esc(name)} sets different limitation periods for contracts, property damage, personal injury, debt, and other claims. The clock can start on different dates, and some claims have special notice requirements. This page does not give a universal deadline because a wrong number is worse than no number.</p>
<p>Check the official statute or the court's own guidance, and ask legal aid if you are close to a deadline. Our <a href="/legal-help/civil-lawsuit-deadlines.html">civil lawsuit deadlines guide</a> explains how to find the rule that applies. Federal claims have their own limits and should be checked separately.</p>
<ul class="links">
{gov_link(s, "court", f"{name} judicial branch: rules and case information", "Official state court system")}
{gov_link(s, "selfhelp", f"{name} court self-help and forms", "Official court self-help page")}
{link_item("Find free legal aid in your state", NATIONAL["lawhelp"][1], "LawHelp.org, a nonprofit legal-aid directory")}
</ul>

<h2>Filing fees and fee waivers</h2>
<p>Filing fees depend on the court, the case type, and the amount in dispute. A fee schedule can change without much notice. Ask the clerk for the current amount for your exact case, and ask whether other costs apply, such as service, copies, or a jury fee.</p>
<p>If you cannot afford the fee, ask for a fee waiver or deferral. Most courts require a form listing income, expenses, and sometimes assets. A waiver can cover the filing fee but usually not the cost of serving the defendant. See our <a href="/legal-help/court-fee-waiver.html">court fee waiver guide</a>.</p>
<ul class="links">
{gov_link(s, "fees", f"{name} filing fees and fee waiver information", "Official court fee page")}
{gov_link(s, "forms", f"{name} court forms", "Official court forms page")}
</ul>

<h2>Serving the defendant in {esc(name)}</h2>
<p>Service is the formal delivery of the complaint and summons. It is not a text, an email, or a social-media message unless the rules specifically allow it. The rules usually require a sheriff, a process server, or another adult who is not a party to the case.</p>
<p><strong>Do not serve the papers yourself</strong> if the state's rules prohibit it. Serving your own case can be treated as improper service and can get the case dismissed. Keep the original affidavit of service and file it with the court.</p>
<p>Read our <a href="/legal-help/serve-court-papers.html">guide to serving court papers</a> and the court's own service rules. If the defendant cannot be found, ask the clerk about alternative service; do not simply skip service.</p>
<ul class="links">
{gov_link(s, "court", f"{name} court rules and procedures", "Official state court system")}
{link_item("Our guide: serve court papers", f"{SITE}/legal-help/serve-court-papers.html", "NFCcop guide")}
</ul>

<h2>Filing online and finding your case afterward</h2>
<p>Some {esc(name)} courts accept electronic filing for self-represented parties; others limit it to attorneys or certain case types. Ask before you rely on a portal.</p>
<ul class="links">
{gov_link(s, "efiling", f"{name} electronic filing information", "Official court e-filing page")}
{gov_link(s, "casesearch", f"{name} online case search", "Official court case lookup")}
</ul>
<p>After filing, ask the clerk for the case number and the judge or division. Check the docket before each hearing, and keep your contact information current with the court.</p>

<h2>Before filing: what to gather</h2>
<ul class="checklist">
<li>Full legal names and current addresses of every party</li>
<li>A plain timeline of what happened, with dates</li>
<li>Contracts, leases, invoices, or written agreements</li>
<li>Photos, videos, and screenshots with dates</li>
<li>Receipts, bank records, and estimates for repairs or losses</li>
<li>Emails, letters, and text messages, saved in full</li>
<li>A written calculation of the money you are asking for</li>
<li>Any notices, demand letters, or termination letters</li>
</ul>
<p>Organize the documents before you go to the clerk. A short index with numbered exhibits makes the filing easier to review and helps you at a hearing.</p>

<h2>Free and low-cost help</h2>
<ul class="links">
{gov_link(s, "selfhelp", f"{name} court self-help center", "Official court self-help page")}
{link_item("Find legal aid in your state", NATIONAL["lawhelp"][1], "LawHelp.org, a nonprofit legal-aid directory")}
{link_item("Legal Services Corporation: find civil legal aid", NATIONAL["lsc"][1], "LSC.gov")}
{link_item("ADA.gov: disability access and accommodations", NATIONAL["ada"][1], "Official federal disability-rights site")}
{link_item("LEP.gov: language access resources", NATIONAL["lep"][1], "Official federal language-access site")}
{link_item("Lawyer referral services", f"{SITE}/legal-help/legal-aid-find-lawyer.html", "NFCcop guide")}
</ul>
<p>Court self-help staff can explain forms but usually cannot give legal advice. Legal aid may help if you qualify by income. A lawyer referral service can connect you with a short consultation, often for a modest fee. If you have a disability or limited English proficiency, ask the court about accommodations and interpreters; those requests are usually free.</p>

<h2>Related guides</h2>
<ul>
<li><a href="/courts/find-a-courthouse-{slug}.html">Find a courthouse in {esc(name)}</a></li>
<li><a href="/legal-help/small-claims-court.html">Small claims court</a></li>
<li><a href="/legal-help/serve-court-papers.html">Serve court papers</a></li>
<li><a href="/legal-help/civil-lawsuit-deadlines.html">Civil lawsuit deadlines</a></li>
<li><a href="/public-records/{slug}.html">{esc(name)} court and public records search</a></li>
<li><a href="/get-help.html">Ask NFCcop for help finding the right office</a></li>
</ul>

<h2>Common questions</h2>
<h3>How much does it cost to file a civil lawsuit in {esc(name)}?</h3>
<p>It depends on the court and the case type. Filing fees, service costs, and copy fees are separate. Ask the clerk for the current fee for your exact case and whether a fee waiver is available.</p>
<h3>Which court do I file in?</h3>
<p>Usually the general trial court for the county where the defendant lives or where the dispute happened, or a limited-jurisdiction court if the amount is small. The correct answer depends on the claim, so confirm with the clerk or legal aid before filing.</p>
<h3>Can I serve the defendant myself?</h3>
<p>Usually not. Most states require service by a sheriff, a process server, or an adult who is not a party to the case. Follow the court's rules and file proof of service.</p>
<h3>How long do I have to sue?</h3>
<p>It depends on the type of claim. {esc(name)} sets different limits for contracts, injury, property, and debt. Check the official statute or ask legal aid; do not rely on a general number you find online.</p>
'''


def warrant_body(s):
    name = s["name"]
    slug = s["slug"]
    search = s["links"].get("casesearch", "")
    warrant = s["links"].get("warrant", "")
    le = s["links"].get("le", "")
    if warrant:
        statewide = f'''<div class="quick-answer"><p><strong>Short answer:</strong> {esc(name)} publishes an official warrant search at <a href="{esc(warrant)}" target="_blank" rel="noopener noreferrer">{esc(warrant.split("//")[-1])}</a>. Use it only to check your own status or an official case record, and confirm anything you find with the court that issued the warrant. A missing result is not proof that no warrant exists.</p></div>'''
        statewide_p = f'''<p>{esc(name)} publishes a statewide warrant search through an official state site. It may not include every warrant, every agency, or every county. Read the site's own disclaimers, and call the issuing court or the county sheriff to confirm.</p>'''
    else:
        statewide = f'''<div class="quick-answer"><p><strong>Short answer:</strong> {esc(name)} does not publish a single statewide public warrant-search tool that we could verify. Warrant records are held by the court that issued the warrant and by the county sheriff or city police. Contact the court clerk directly for your own case.</p></div>'''
        statewide_p = f'''<p>We could not verify a statewide, official warrant search for {esc(name)}. That is normal. Warrants are issued by judges in local cases and stored by the court and the arresting agency. Some counties publish a jail roster or a wanted list; many do not publish warrants at all. A commercial "warrant search" site is not an official source and cannot confirm whether a warrant exists.</p>'''
    return f'''
<p>If you think there may be a warrant with your name on it, the safest step is to contact the court or a lawyer, not to call around or ask someone else to check for you. This page explains where official {esc(name)} records are kept, what the different warrant types mean, and why an online "no result" can be wrong.</p>
<p>This page is for people checking their own status or an official case record. It does not list names, photos, or addresses of anyone with an alleged warrant, and it does not help anyone avoid law enforcement.</p>
{fig(slug, name, "warrant")}
{statewide}
{statewide_p}
<ul class="links">
{link_item(f"{name} judicial branch: official court information", s["links"]["court"], "Official state court system") if s["links"].get("court") else ""}
{gov_link(s, "casesearch", f"{name} online court case search", "Official court case lookup")}
{gov_link(s, "warrant", f"{name} official warrant search", "Official state warrant site")}
{gov_link(s, "le", f"{name} state law-enforcement agency", "Official state agency")}
{link_item("USA.gov: find your county sheriff or local government", NATIONAL["localgov"][1], "Official federal directory")}
</ul>

<h2>Warrant records are usually kept locally</h2>
<p>A warrant is a court order. It is issued by a judge in a specific case, in a specific county or city. The court clerk keeps the case file. The sheriff or police department keeps the arrest record. There is often no single office that can see every warrant in the state.</p>
<p>That means the county matters. If you were arrested, cited, or told to appear in a particular court, start there. If you do not know the county, work backward from where the event happened, where you lived, or where the case was filed.</p>

<h2>How to identify the county that may hold the record</h2>
<ul>
<li><strong>Where were you arrested or cited?</strong> The arresting agency and the local court are the first places to check.</li>
<li><strong>Where did the case happen?</strong> A charge is usually filed in the county where the conduct allegedly occurred.</li>
<li><strong>Where do you live?</strong> A failure-to-appear warrant is usually issued by the court you missed, not by the court near your home.</li>
<li><strong>Do you have a case number?</strong> Any letter, citation, or booking sheet can point to the right clerk.</li>
</ul>
<p>If you are unsure, call the clerk of the court you think is involved and ask how to check your own case. Write down the name of the person you speak with and the date.</p>

<h2>Four kinds of warrants, and what they mean</h2>
<div class="table-wrap">
<table>
<thead><tr><th scope="col">Type</th><th scope="col">What it usually means</th></tr></thead>
<tbody>
<tr><td>Arrest warrant</td><td>A judge has authorized police to arrest a person based on probable cause in a criminal case.</td></tr>
<tr><td>Bench warrant</td><td>A judge issues it from the bench, often for missing a court date, failing to comply with an order, or violating a condition of release.</td></tr>
<tr><td>Failure-to-appear warrant</td><td>A warrant issued after a person does not show up for a required hearing. It may be called a bench warrant or an FTA warrant.</td></tr>
<tr><td>Search warrant</td><td>Permission to search a place or seize property. It is not an arrest warrant, and it is often sealed while the investigation is active.</td></tr>
</tbody>
</table>
</div>
<p>A "wanted" notice, a jail roster, and a warrant are different things. A person can appear on a jail roster without an open warrant, and a warrant can exist without any public listing.</p>

<h2>What online records can and cannot tell you</h2>
<ul>
<li><strong>Not every warrant is public.</strong> Sealed cases, juvenile matters, and active investigations may be hidden by law.</li>
<li><strong>Information can be delayed.</strong> A warrant may be issued, recalled, or served before a website updates.</li>
<li><strong>Records can be incomplete.</strong> Small agencies may not publish anything online.</li>
<li><strong>Records can be removed.</strong> A dismissed case or recalled warrant may disappear, or may linger after it is no longer active.</li>
<li><strong>A "no result" is not proof.</strong> A name may be misspelled, a middle name may be missing, or the record may sit in a different county.</li>
<li><strong>Names can match the wrong person.</strong> Never confront or accuse someone based on a website result.</li>
</ul>
<div class="warning"><strong>Online information may be out of date.</strong> Even an official court portal can lag. Confirm with the clerk or the issuing court before you act on anything you see.</div>

<h2>Safer next steps if you think there is a warrant</h2>
<ol>
<li><strong>Contact the court clerk.</strong> Ask how to check your own case and whether a warrant is active. You do not have to explain your whole situation on the phone.</li>
<li><strong>Talk to a defense lawyer.</strong> A lawyer can check the docket, explain the warrant, and tell you about options such as appearing, recalling the warrant, or asking for a new date.</li>
<li><strong>Contact a public defender if you are eligible.</strong> Eligibility is based on income and the type of case. Ask the court or the local public defender's office.</li>
<li><strong>Contact legal aid.</strong> Legal aid usually does not defend criminal cases, but it can help with related housing, benefits, or family problems.</li>
<li><strong>Keep a written record.</strong> Note the court, case number, date, and who you spoke with. If you hire a lawyer, bring it to the first meeting.</li>
</ol>
<ul class="links">
{link_item("Find legal aid in your state", NATIONAL["lawhelp"][1], "LawHelp.org, a nonprofit legal-aid directory")}
{link_item("Find a lawyer through a legal-aid or referral service", f"{SITE}/legal-help/legal-aid-find-lawyer.html", "NFCcop guide")}
{link_item("Find a courthouse in {0}".format(name), f"{SITE}/courts/find-a-courthouse-{slug}.html", "NFCcop guide")}
</ul>

<h2>Safety notice</h2>
<div class="safety"><p><strong>Do not confront another person about an alleged warrant.</strong> Do not go to a home, workplace, or school to demand answers, and do not post someone's name or photo online. If you believe a person is dangerous, call 911. If you believe you have a warrant, contact the court or a lawyer rather than trying to resolve it informally.</p></div>
<p>This page does not tell anyone how to evade, hide from, or interfere with law enforcement. If there is an active warrant, the legal path is to appear, get advice, and ask the court about the options that apply to your case.</p>

<h2>Related guides</h2>
<ul>
<li><a href="/public-records/{slug}.html">{esc(name)} court and public records search</a></li>
<li><a href="/courts/find-a-courthouse-{slug}.html">Find a courthouse in {esc(name)}</a></li>
<li><a href="/probate/{slug}.html">{esc(name)} probate records</a></li>
<li><a href="/legal-help/legal-aid-find-lawyer.html">Find legal aid or a lawyer</a></li>
<li><a href="/get-help.html">Ask NFCcop for help finding the right office</a></li>
</ul>

<h2>Common questions</h2>
<h3>Is there a statewide warrant search in {esc(name)}?</h3>
<p>{("Yes. " + esc(name) + " publishes an official statewide warrant search through its courts. It may not include every agency or every warrant, so confirm with the issuing court.") if warrant else ("No. We could not verify a statewide public warrant search for " + esc(name) + ". Warrants are held by the issuing court and local law enforcement, so contact the county clerk or sheriff for your own case.")}</p>
<h3>Can I check my own warrant status online?</h3>
<p>Sometimes. A court case search may show a criminal case and a warrant, but coverage varies. The most reliable check is to call the clerk of the court handling your case and ask about your own record.</p>
<h3>Does "no results" mean there is no warrant?</h3>
<p>No. Records can be delayed, sealed, incomplete, or filed under a different name or county. Only the issuing court or agency can confirm whether a warrant is active.</p>
<h3>Should I call the police to ask about a warrant?</h3>
<p>You can ask the court clerk first. If you call a police department, use its published non-emergency number, not 911. Do not give personal information to a caller who contacts you demanding payment to "clear a warrant"; that is a common scam.</p>
'''


# ------------------------------------------------------------------- builders

def build_state_pages():
    written = []
    for slug, s in STATES.items():
        s = dict(s)
        s["slug"] = slug
        name = s["name"]

        probate_faq = [
            (f"Which court handles probate in {name}?",
             f"{s['probate']} Confirm the county and court with the official {name} court directory before filing or requesting records."),
            (f"Are all {name} probate records online?",
             "No. Some courts post case indexes or scanned documents, but many probate files are available only from the county probate clerk. A missing online record does not mean an estate was never opened."),
            (f"How do I get a copy of a probate record in {name}?",
             "Contact the probate clerk in the county where the person lived. Give the full legal name, date of death, approximate filing year, and case number if you have one. Ask about copy and certification fees before ordering."),
            (f"Does {name} have a small-estate process?",
             f"{s['small']} Limits, waiting periods, and forms change, so confirm the current rule with the court or the official court website."),
        ]
        body = probate_body(s)
        path = f"probate/{slug}.html"
        title = f"{name} Probate Records and Court Research: Official Free Resources"
        desc = f"Find {name} probate records for free: which court handles estates, how to search a case, request copies of a will or inventory, and use the small-estate process."
        page = shell(
            s, url_path=path, title=title, description=desc,
            h1=f"{name} Probate Records and Court Research: Official Free Resources",
            crumbs=[("Home", "/"), ("Probate by state", "/probate/"), (name, None)],
            body=body, faq=probate_faq, topic="probate",
        )
        write(path, page)
        written.append(path)

        courts_faq = [
            (f"How do I find the right courthouse in {name}?",
             f"Use the official {name} judicial branch directory, choose the county, and confirm the address and phone number on the court's own page. Call the clerk before you travel."),
            (f"Where do I file if I live in a different county?",
             "It depends on the case. Probate usually follows the deceased person's county; property cases often follow the property; civil disputes may follow the defendant or where the events happened. Confirm with the clerk or legal aid."),
            (f"Can I file by mail or online in {name}?",
             "Often yes, but not for every case type. Ask the clerk whether your court accepts mail, e-filing, or a drop box, and whether an original signature is required."),
            (f"What should I ask the court clerk?",
             "Ask whether this is the right court for your case, which county to file in, the current filing fee, whether a fee waiver exists, which forms to use, and how to get an interpreter or disability accommodation."),
        ]
        body = courts_body(s)
        path = f"courts/find-a-courthouse-{slug}.html"
        title = f"Find a Courthouse in {name}: Official Court and Clerk Directories"
        desc = f"Official {name} court directory, court structure explained, how to pick the right county, and a checklist to confirm address, hours, filing, and access before you go."
        page = shell(
            s, url_path=path, title=title, description=desc,
            h1=f"Find a Courthouse in {name}: Official Court and Clerk Directories",
            crumbs=[("Home", "/"), ("Courts", "/courts/"), (name, None)],
            body=body, faq=courts_faq, topic="courts",
        )
        write(path, page)
        written.append(path)

        civil_faq = [
            (f"How much does it cost to file a civil lawsuit in {name}?",
             "It depends on the court and the case type. Filing, service, and copy fees are separate. Ask the clerk for the current fee for your exact case and whether a fee waiver is available."),
            (f"Which court do I file in?",
             f"{s['civil']} Confirm with the clerk or legal aid before filing, because filing in the wrong court can cost a fee and delay the case."),
            (f"Can I serve the defendant myself in {name}?",
             "Usually not. Most states require service by a sheriff, a process server, or an adult who is not a party to the case. Follow the court's rules and file proof of service."),
            (f"How long do I have to sue?",
             f"{name} sets different deadlines for different claims, and this page does not give a universal number. Check the official statute or ask legal aid before the deadline passes."),
        ]
        body = civil_body(s)
        path = f"legal-help/file-a-civil-lawsuit-{slug}.html"
        title = f"How to File a Civil Lawsuit in {name}: Courts, Forms, Fees, and Service"
        desc = f"Step-by-step guide to filing a civil lawsuit in {name}: choosing the court and county, complaint forms, filing fees and waivers, service of process, and free legal help."
        page = shell(
            s, url_path=path, title=title, description=desc,
            h1=f"How to File a Civil Lawsuit in {name}: Courts, Forms, Fees, and Service",
            crumbs=[("Home", "/"), ("Legal help", "/legal-help/"), (name, None)],
            body=body, faq=civil_faq, topic="civil",
        )
        write(path, page)
        written.append(path)

        warrant_faq = [
            (f"Is there a statewide warrant search in {name}?",
             (f"Yes. {name} publishes an official statewide warrant search through its courts. It may not include every agency or every warrant, so confirm with the issuing court." if s["links"].get("warrant")
              else f"No. We could not verify a statewide public warrant search for {name}. Warrants are held by the issuing court and local law enforcement, so contact the county clerk or sheriff for your own case.")),
            (f"Can I check my own warrant status online?",
             "Sometimes. A court case search may show a criminal case and a warrant, but coverage varies. The most reliable check is to call the clerk of the court handling your case and ask about your own record."),
            (f"Does no result mean there is no warrant?",
             "No. Records can be delayed, sealed, incomplete, or filed under a different name or county. Only the issuing court or agency can confirm whether a warrant is active."),
            (f"What should I do if I think there is a warrant for me?",
             "Contact the court clerk or a defense lawyer. If you cannot afford a lawyer, ask about a public defender or legal aid. Do not ignore a court date, and do not confront anyone based on an online record."),
        ]
        body = warrant_body(s)
        path = f"public-records/warrant-information-{slug}.html"
        title = f"Check Warrant Information in {name}: Official Court and Law-Enforcement Sources"
        desc = f"Official {name} warrant information: whether a statewide search exists, how warrant records are kept by county courts and sheriffs, and safer next steps if you think you have a warrant."
        page = shell(
            s, url_path=path, title=title, description=desc,
            h1=f"Check Warrant Information in {name}: Official Court and Law-Enforcement Sources",
            crumbs=[("Home", "/"), ("Public records", "/public-records/"), (name, None)],
            body=body, faq=warrant_faq, topic="warrant",
        )
        write(path, page)
        written.append(path)
    return written


def write(path, content):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


def build_hubs():
    ordered = sorted(STATES.items(), key=lambda kv: kv[1]["name"])
    grid = "\n".join(
        f'<a href="/probate/{slug}.html">{esc(s["name"])}</a>' for slug, s in ordered
    )
    probate_hub = shell(
        {"name": "the United States", "slug": "alabama", "links": {}},
        url_path="probate/index.html",
        title="Probate Records by State: Official Free Court Resources | NFCcop",
        description="Choose your state to find the probate court, search estate cases, request wills and inventories, and use the small-estate process. Official free sources only.",
        h1="Probate Records by State: Official Free Court Resources",
        crumbs=[("Home", "/"), ("Probate by state", None)],
        body=f'''
<p>Probate is handled county by county, and every state organizes its courts differently. Choose a state to see which court keeps estate files, how to search for a case, and how to request a copy of a will, inventory, or closing order.</p>
<div class="quick-answer"><p><strong>Before you start:</strong> gather the person's full legal name, approximate date of death, county of residence, any case number, and the name of the executor or administrator.</p></div>
<h2>Choose a state</h2>
<div class="state-grid">
{grid}
</div>
<h2>What every state page covers</h2>
<ul>
<li>Which court handles probate, and how to find the right county</li>
<li>How to search for a case and when you must call the clerk</li>
<li>How to request copies of the petition, will, letters, inventory, accounting, and closing order</li>
<li>The small-estate or simplified process, with a warning that limits change</li>
<li>Official forms, self-help centers, and free legal aid</li>
</ul>
<p>Start with the <a href="/public-records/">public records directory</a> if you also need property, business, or inmate records, or read <a href="/legal-help/small-estate-affidavit.html">how small estates work</a>.</p>
<h2>Common questions</h2>
<h3>Are probate records free to search?</h3>
<p>Often the index is free and copies cost money. Some courts charge for online access. Fees vary by county, so ask the clerk before ordering.</p>
<h3>Can I find a will online?</h3>
<p>Sometimes, but many wills are only in the court file. A filed will may be available from the probate clerk; a will kept at home or with a lawyer may never be filed.</p>
<h3>Do I need a lawyer to open an estate?</h3>
<p>Not always. Simple estates are often handled without one. Contested wills, minor heirs, businesses, or unclear home titles are good reasons to get advice.</p>
''',
        og_image=f"{SITE}/assets/og-default.png",
        faq=[
            ("Are probate records free to search?", "Often the index is free and copies cost money. Some courts charge for online access. Fees vary by county, so ask the clerk before ordering."),
            ("Can I find a will online?", "Sometimes, but many wills are only in the court file. A filed will may be available from the probate clerk; a will kept at home or with a lawyer may never be filed."),
            ("Do I need a lawyer to open an estate?", "Not always. Simple estates are often handled without one. Contested wills, minor heirs, businesses, or unclear home titles are good reasons to get advice."),
        ],
        topic="probate",
    )
    write("probate/index.html", probate_hub)

    grid = "\n".join(
        f'<a href="/courts/find-a-courthouse-{slug}.html">{esc(s["name"])}</a>' for slug, s in ordered
    )
    courts_hub = shell(
        {"name": "the United States", "slug": "alabama", "links": {}},
        url_path="courts/index.html",
        title="Find a Courthouse by State: Official Court and Clerk Directories | NFCcop",
        description="Choose your state for the official court directory, a plain-language guide to court structure, and a checklist to confirm the right county, address, hours, and access.",
        h1="Find a Courthouse by State: Official Court and Clerk Directories",
        crumbs=[("Home", "/"), ("Courts", None)],
        body=f'''
<p>Court names differ by state, and the right building depends on the type of case and the county. Choose a state for the official directory and a checklist to confirm the address, hours, filing window, accessibility, e-filing, and remote hearings.</p>
<div class="quick-answer"><p><strong>Confirm before you travel:</strong> courts move and consolidate. Call the clerk or check the court's own page for the address and the last time a filing is accepted.</p></div>
<h2>Choose a state</h2>
<div class="state-grid">
{grid}
</div>
<h2>What every state page covers</h2>
<ul>
<li>The official state court directory and clerk contacts</li>
<li>How the state's courts are organized, in plain language</li>
<li>How to choose the right county when residence, the event, property, and the defendant point to different places</li>
<li>What to verify by phone, including accessibility and language access</li>
<li>Questions to ask the clerk before filing</li>
</ul>
<p>If you are filing an estate, start with the <a href="/probate/">probate guide for your state</a>. If you are suing someone, read <a href="/legal-help/file-a-civil-lawsuit-california.html">how civil filing works</a> (available for every state from the <a href="/legal-help/">legal help hub</a>).</p>
<h2>Common questions</h2>
<h3>How do I know which court handles my case?</h3>
<p>The type of case and the amount in dispute usually decide. Court staff can explain where cases are filed, but they cannot give legal advice. Confirm with the clerk or a legal-aid program.</p>
<h3>What if I file in the wrong county?</h3>
<p>The court may transfer the case or dismiss it, and you may lose a filing fee or time. Ask the clerk before filing if you are unsure.</p>
<h3>Are court addresses online always current?</h3>
<p>No. Verify the address and hours on the court's own page or by phone, especially before traveling to a satellite or annex building.</p>
''',
        og_image=f"{SITE}/assets/og-default.png",
        faq=[
            ("How do I know which court handles my case?", "The type of case and the amount in dispute usually decide. Court staff can explain where cases are filed, but they cannot give legal advice. Confirm with the clerk or a legal-aid program."),
            ("What if I file in the wrong county?", "The court may transfer the case or dismiss it, and you may lose a filing fee or time. Ask the clerk before filing if you are unsure."),
            ("Are court addresses online always current?", "No. Verify the address and hours on the court's own page or by phone, especially before traveling to a satellite or annex building."),
        ],
        topic="courts",
    )
    write("courts/index.html", courts_hub)


def update_sitemap(paths):
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    add = []
    text = text.replace(f"{SITE}/probate/index.html", f"{SITE}/probate/")
    text = text.replace(f"{SITE}/courts/index.html", f"{SITE}/courts/")
    for p in paths:
        loc = f"{SITE}/" + (p[: -len("index.html")] if p.endswith("index.html") else p)
        if loc in text:
            continue
        add.append(f"<url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>")
    if not add:
        return 0
    text = text.replace("</urlset>", "\n".join(add) + "\n</urlset>")
    sm.write_text(text, encoding="utf-8")
    return len(add)


def inject_hubs():
    """Add state link grids to the existing public-records and legal-help hubs."""
    ordered = sorted(STATES.items(), key=lambda kv: kv[1]["name"])
    pr = ROOT / "public-records/index.html"
    text = pr.read_text(encoding="utf-8")
    marker = "<h2>Choose a state"
    if "warrant-information-alabama" not in text:
        grid = "\n".join(
            f'<a href="/public-records/warrant-information-{slug}.html">{esc(s["name"])}</a>'
            for slug, s in ordered
        )
        block = f'''<style>.state-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.5rem;margin:1rem 0 2rem}}.state-grid a{{display:block;border:1px solid #cbd5e1;border-radius:8px;padding:.6rem .75rem;text-decoration:none;background:#fff;color:#0369a1}}</style>
<h2>Warrant information by state</h2>
<p>Warrant records are usually kept by the issuing court and the county sheriff, not by one state office. Choose a state to see whether an official statewide search exists and how to check your own case safely.</p>
<div class="state-grid">
{grid}
</div>
'''
        if marker in text:
            text = text.replace(marker, block + marker, 1)
            pr.write_text(text, encoding="utf-8")

    lh = ROOT / "legal-help/index.html"
    text = lh.read_text(encoding="utf-8")
    marker = '<h2 id="self-help-guides">Self-help guides</h2>'
    if "file-a-civil-lawsuit-alabama" not in text and marker in text:
        grid = "\n".join(
            f'<a href="/legal-help/file-a-civil-lawsuit-{slug}.html">{esc(s["name"])}</a>'
            for slug, s in ordered
        )
        block = f'''<style>.state-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.5rem;margin:1rem 0 2rem}}.state-grid a{{display:block;border:1px solid #cbd5e1;border-radius:8px;padding:.6rem .75rem;text-decoration:none;background:#fff;color:#0369a1}}</style>
<h2>File a civil lawsuit, state by state</h2>
<p>Each state guide explains which court hears civil cases, how to choose the county, where to get the complaint forms, filing fees and waivers, service of process, and free legal help.</p>
<div class="state-grid">
{grid}
</div>
'''
        text = text.replace(marker, block + marker, 1)
        lh.write_text(text, encoding="utf-8")


def main():
    paths = build_state_pages()
    build_hubs()
    paths += ["probate/index.html", "courts/index.html"]
    inject_hubs()
    added = update_sitemap(paths)
    print(f"wrote {len(paths)} pages; added {added} sitemap entries")


if __name__ == "__main__":
    main()
