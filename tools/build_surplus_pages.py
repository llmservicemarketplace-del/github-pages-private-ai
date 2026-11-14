#!/usr/bin/env python3
"""Build the /government-auctions/ section: surplus property, tax sales and
government real estate, federal + state + local.

Outputs:
  government-auctions/index.html                       hub, state grid
  government-auctions/{state}.html                     50 state pages
  government-auctions/federal-surplus-auctions.html
  government-auctions/federal-real-estate-for-sale.html
  government-auctions/tax-sales-explained.html
  government-auctions/city-county-surplus-auctions.html
  government-auctions/surplus-property-for-nonprofits.html

If tools/surplus-links.json exists (written by harvest_surplus_links.py, which
only keeps URLs that answered and mention surplus), each state page also links
straight to the state surplus website and says how that state sells to the
public. The file was built on 2026-11-14 from live search results for each
state's official surplus pages. Without it, pages give the agency name and
phone from the GSA list.

Run from the repo root:  python tools/build_surplus_pages.py
Safe to re-run: injections are marker-guarded.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_state_resource_pages as G
from surplus_data import SASP, TAX, KIND_TEXT, FEDERAL_REAL_ESTATE, FEDERAL_AUCTIONS

esc, ext, row, link_item, shell, write = G.esc, G.ext, G.row, G.link_item, G.shell, G.write
DIR = "government-auctions"
CRUMB = ("Government auctions", f"/{DIR}/")
REVIEWED = G.REVIEWED
LINKS_FILE = ROOT / "tools" / "surplus-links.json"
STATE_LINKS = json.loads(LINKS_FILE.read_text(encoding="utf-8")) if LINKS_FILE.exists() else {}

GUIDES = [
    ("federal-surplus-auctions.html", "Federal surplus and seized property auctions"),
    ("federal-real-estate-for-sale.html", "Federal real estate for sale"),
    ("tax-sales-explained.html", "Tax lien and tax deed sales explained"),
    ("city-county-surplus-auctions.html", "City and county surplus auctions"),
    ("surplus-property-for-nonprofits.html", "Surplus property for nonprofits"),
]

SCAM = '''<div class="safety"><strong>Do not pay for a list.</strong> Government sale lists are free on the government's own website. Sites that charge a fee or a subscription for "government foreclosure lists" or "secret auction access" are selling public information. Start from a .gov address or the office's own page, and follow its link to the auction.</div>'''

RISKS = '''<ul>
<li><strong>Sold as-is.</strong> There is usually no inspection, no warranty, and no refund. For real estate you often cannot go inside before you bid.</li>
<li><strong>Title is your job.</strong> Some liens, easements, and other claims can survive a sale. A title search before bidding is the only way to know. Title insurance can be hard to get on tax-sale property without more legal work.</li>
<li><strong>People may live there.</strong> If the property is occupied, removing anyone takes a court process that you pay for.</li>
<li><strong>Payment is fast.</strong> Many sales want a deposit that day and the balance within days, by certified funds.</li>
<li><strong>Costs keep coming.</strong> Later taxes, code violations, demolition orders, and cleanup can follow the property to the buyer.</li>
<li><strong>Buyer's fees.</strong> Online auctions often add a buyer's premium on top of the bid.</li>
</ul>'''


def fed_rows(items):
    return "\n".join(
        f"<tr><td>{ext(url, label)}</td><td>{esc(owner)}</td><td>{esc(what)}</td></tr>"
        for label, url, owner, what in items
    )


def fed_table(items):
    return f'<div class="table-wrap"><table><tr><th>Where to look</th><th>Run by</th><th>What it sells</th></tr>\n{fed_rows(items)}\n</table></div>'


def guides_list(skip=None):
    items = "".join(
        f'<li><a href="/{DIR}/{f}">{esc(t)}</a></li>' for f, t in GUIDES if f != skip
    )
    return f'<h2>More on government sales</h2>\n<ul>{items}<li><a href="/{DIR}/">Government auctions by state</a></li></ul>'


# ------------------------------------------------------------- state pages

def state_page(hub):
    name, slug = hub["name"], hub["slug"]
    agency, phone = SASP[slug]
    kind, who, note = TAX[slug]
    kind_label, kind_text = KIND_TEXT[kind]
    kind_text = kind_text.format(name=name)
    local_unit = {"louisiana": "parish", "alaska": "borough"}.get(slug, "county")
    link = STATE_LINKS.get(slug, {})
    surplus_url = link.get("url")
    how = link.get("how", "")
    land_url, land_label = link.get("land_url"), link.get("land_label")
    land_row = row("State-owned real estate", ext(land_url, land_label)) if land_url else ""
    surplus_row = row("State surplus website", ext(surplus_url, f"{name} state surplus property")) if surplus_url else ""
    faq = [
        (f"Where can I buy government surplus in {name}?",
         (how + " " if how else "") + f"The state surplus office is {agency}, {phone}. Also check your city and {local_unit} websites for their own surplus auctions, and search GSA Auctions by state for federal surplus."),
        (f"Is {name} a tax lien state or a tax deed state?",
         kind_text + (" " + note if note else "")),
        (f"Who runs tax sales in {name}?",
         f"Tax sales are run by {who}. Sale dates, bidder registration, and the list of properties come from that office, and the list is free."),
        (f"How do I find foreclosure and sheriff's sales in {name}?",
         f"Mortgage foreclosure and judgment sales are announced by the sheriff, the court, or a trustee, and published as legal notices. Check the {local_unit} sheriff's website and the court clerk for the {local_unit} where the property sits."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> In {esc(name)} there are four places to look. State surplus goes through <strong>{esc(agency)}</strong> ({esc(phone)}). Tax-delinquent real estate is sold by <strong>{esc(who)}</strong>. Foreclosure and sheriff's sales are run {esc(local_unit)} by {esc(local_unit)}. Federal property in {esc(name)} is listed on federal sites you can search by state.</p>
<p>Every official list is free. You should never have to pay to see what is for sale.</p>
</div>
<p>Governments sell things they no longer need and property they have taken for unpaid taxes or through court cases. That includes vehicles, equipment, office furniture, vacant lots, houses, and land. This page maps who sells what in {esc(name)} at the state, local, and federal level, and what to check before you bid.</p>
{G.fig(slug, name, "State surplus is sold by a state agency. Tax sales and sheriff's sales are local.")}

<h2>{esc(name)} at a glance</h2>
<div class="table-wrap"><table class="dir">
{row("State surplus office", f"{esc(agency)}<br>Phone: <strong>{esc(phone)}</strong>")}
{surplus_row}
{land_row}
{row("Tax-delinquent real estate", f"{esc(kind_label[0].upper() + kind_label[1:])}. Run by {esc(who)}.")}
{row("Foreclosure and sheriff's sales", f"The {esc(local_unit)} sheriff, the court, or a trustee, depending on the case")}
{row("City and " + local_unit + " surplus", "Each government's purchasing, fleet, or finance office")}
{row("Federal surplus in " + name, ext("https://gsaauctions.gov/", "GSA Auctions") + " (search by state)")}
{row("Federal homes in " + name, ext("https://www.hudhomestore.gov/Home/Index.aspx", "HUD Home Store") + " (search by state)")}
{row("Property records", f'<a href="/public-records/{slug}.html">{esc(name)} public records guide</a>')}
</table></div>
{SCAM}

<h2>State surplus property in {esc(name)}</h2>
<p>The federal government lists <strong>{esc(agency)}</strong> as {esc(name)}'s state agency for surplus property. Phone: <strong>{esc(phone)}</strong>.</p>
{f'<p><strong>How {esc(name)} sells to the public:</strong> {esc(how)} Start at {ext(surplus_url, name + " state surplus property (official site)")}.</p>' if surplus_url and how else ""}
<p>The office listed by GSA runs the federal surplus program for local governments and eligible nonprofits. In most states the same office, or one beside it, also sells the state's own surplus to the public: retired vehicles, heavy equipment, computers, furniture, and tools. Ask three questions when you call:</p>
<ul>
<li>How does the public buy state surplus: a warehouse store, online auctions, or live auctions?</li>
<li>Which website carries the listings, and do I need to register first?</li>
<li>Does the state sell surplus real estate, and which agency handles it?</li>
</ul>
<p>State land and buildings are usually sold by a different agency than equipment. The transportation department often sells leftover right-of-way parcels, and a land office or general services agency may sell other state real estate.{f" In {esc(name)}, see {ext(land_url, land_label)}." if land_url else ""}</p>
<p>The state treasurer or comptroller also auctions unclaimed property from abandoned safe deposit boxes from time to time. Find {esc(name)}'s program through {ext("https://unclaimed.org/", "unclaimed.org")}, and check it for money owed to you while you are there.</p>

<h2>Tax-delinquent property in {esc(name)}</h2>
<p>{esc(kind_text)}</p>
{f"<p>{esc(note)}</p>" if note else ""}
<p><strong>Who runs it:</strong> {esc(who)}. That office publishes the sale date, the list of parcels, bidder registration rules, and how to pay. Dates, redemption periods, and interest rates are set by state law and change, so take them from the office's current notice and not from an investing website.</p>
<p>Before you bid on any parcel:</p>
<ol>
<li><strong>Read the official notice and terms</strong> for that sale, start to finish.</li>
<li><strong>Look up the parcel.</strong> Use the assessor's and recorder's records to see the owner, the legal description, and what is recorded against it. See the <a href="/public-records/{slug}.html">{esc(name)} public records guide</a>.</li>
<li><strong>Go look at it</strong> from the street. Vacant lots, landlocked strips, and condemned buildings are common on tax sale lists.</li>
<li><strong>Find out what survives the sale.</strong> Ask a title company or a real estate lawyer which liens and claims stay with the property.</li>
<li><strong>Know the owner's rights.</strong> Learn whether the former owner can redeem after the sale, and for how long.</li>
</ol>
<p>For how the three systems differ, see <a href="/{DIR}/tax-sales-explained.html">tax lien and tax deed sales explained</a>.</p>

<h2>Foreclosure and sheriff's sales</h2>
<p>These are separate from tax sales. A lender forecloses on a mortgage, or a creditor collects a court judgment, and the property is sold at public auction. Depending on the case, the sale is held by the {esc(local_unit)} sheriff, a court officer, or a trustee named in the loan papers.</p>
<ul>
<li>Sales are announced as legal notices and usually posted on the sheriff's or court's website.</li>
<li>The court file shows what is owed and who has a claim. See <a href="/courts/find-a-courthouse-{slug}.html">find a courthouse in {esc(name)}</a>.</li>
<li>After a foreclosure, the bank or federal agency that ends up with the house sells it through regular listings. See <a href="/moving-on/foreclosed-reo-property-research/">researching foreclosed and bank-owned property</a>.</li>
</ul>

<h2>City, {esc(local_unit)}, and other local sales</h2>
<p>Local governments in {esc(name)} sell their own surplus. There is no single statewide list, so check each one:</p>
<ul>
<li><strong>Cities and {esc(local_unit)} governments:</strong> retired police cars, trucks, mowers, and office equipment, through the purchasing, fleet, or finance office.</li>
<li><strong>Police and sheriff's departments:</strong> unclaimed, found, and forfeited property.</li>
<li><strong>School districts, colleges, and utilities:</strong> buses, computers, kitchen and shop equipment.</li>
<li><strong>Land banks and city-owned lots:</strong> many cities sell vacant lots and houses they hold, sometimes to neighbors or to buyers who agree to repair them.</li>
<li><strong>Housing and redevelopment agencies:</strong> lots and buildings offered for redevelopment.</li>
</ul>
<p>To find them, go to the government's own website and search for "surplus," "auction," or "purchasing." Many use an outside online auction company to run the bidding. That is normal, but reach it through the link on the government's own site so you know the sale is real. Find local government sites through {ext("https://www.usa.gov/local-governments", "USA.gov's local government directory")}. More in <a href="/{DIR}/city-county-surplus-auctions.html">city and county surplus auctions</a>.</p>

<h2>Federal property for sale in {esc(name)}</h2>
<p>These federal sites list property nationwide. Use the state filter for {esc(name)}.</p>
{fed_table(FEDERAL_AUCTIONS + FEDERAL_REAL_ESTATE)}
<p>Details: <a href="/{DIR}/federal-surplus-auctions.html">federal surplus auctions</a> and <a href="/{DIR}/federal-real-estate-for-sale.html">federal real estate for sale</a>.</p>

<h2>What to check before you bid on anything</h2>
{RISKS}

<h2>If you run a nonprofit or work for a local government</h2>
<p>You may not need to bid at all. Eligible nonprofits and public agencies can get federal surplus through {esc(agency)} for a service charge instead of the market price. See <a href="/{DIR}/surplus-property-for-nonprofits.html">surplus property for nonprofits</a>.</p>

<h2>If it is your property being sold</h2>
<p>If your home is headed to a tax sale or foreclosure, you may still be able to pay, set up a payment plan, or redeem after the sale. If a tax sale brings more than you owed, you may have a claim to the extra money. Act early and get free advice: <a href="/legal-help/free-legal-aid-{slug}.html">free legal aid in {esc(name)}</a> and <a href="/moving-on/mortgage-forbearance/">mortgage forbearance</a>.</p>

<h2>Official links</h2>
<ul class="links">
{link_item(f"{name} state surplus property", surplus_url, "Official state surplus website") if surplus_url else ""}
{link_item(land_label, land_url, "Official state real estate sales page") if land_url else ""}
{link_item("GSA list of state agencies for surplus property", "https://gsa.gov/sasp", "U.S. General Services Administration. Source for the agency and phone above.")}
{link_item("USA.gov: government auctions of seized and surplus property", "https://www.usa.gov/auctions-and-sales", "Official U.S. government guide")}
{link_item("USA.gov: real estate and federal lands for sale", "https://www.usa.gov/real-estate-sales", "Official U.S. government guide")}
{link_item("USA.gov: local governments", "https://www.usa.gov/local-governments", "Find your city and county websites")}
</ul>
{G.faq_html(faq)}
<h2>More {esc(name)} guides</h2>
<ul class="more-state">
<li><a href="/states/{slug}.html">{esc(name)} help guide (all topics)</a></li>
<li><a href="/public-records/{slug}.html">{esc(name)} public records</a></li>
<li><a href="/courts/find-a-courthouse-{slug}.html">Find a courthouse in {esc(name)}</a></li>
<li><a href="/probate/{slug}.html">Probate in {esc(name)}</a></li>
<li><a href="/legal-help/small-claims-court-{slug}.html">Small claims court in {esc(name)}</a></li>
<li><a href="/{DIR}/">Government auctions in other states</a></li>
</ul>
'''
    return dict(
        title=f"{name} Government Surplus and Tax Sale Auctions | NFCcop",
        description=f"Where to buy government surplus and real estate in {name}: the state surplus office and phone, who runs tax sales, sheriff's sales, city and {local_unit} auctions, and federal property.",
        h1=f"{name} Government Auctions: Surplus Property, Tax Sales, and Real Estate",
        body=body, faq=faq,
    )


# ------------------------------------------------------------ national guides

def guide_federal_surplus(hubs):
    faq = [
        ("Where does the federal government sell surplus property?",
         "Mainly on GSA Auctions, which lists federal surplus vehicles, equipment, furniture, and electronics by state. The Treasury Department and the U.S. Marshals Service sell seized and forfeited property through their own programs."),
        ("Can anyone bid at a federal surplus auction?",
         "Generally yes. Most federal auctions are open to the public once you register on the auction site. Each sale has its own terms on payment, pickup, and who may bid."),
        ("Are government auction lists free?",
         "Yes. Federal agencies post their sales for free. You do not need to buy a list or a membership."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Most federal surplus is sold online at {ext("https://gsaauctions.gov/", "GSA Auctions")}, where you can filter by state. Seized and forfeited property is sold through the Treasury Department and the U.S. Marshals Service. All of the listings are free to view.</p>
</div>
<p>Federal agencies sell what they no longer need and what the government has seized. This page lists the official places to look, how bidding works, and what to watch for. For houses and land, see <a href="/{DIR}/federal-real-estate-for-sale.html">federal real estate for sale</a>.</p>
{SCAM}
<h2>Official federal auction sites</h2>
{fed_table(FEDERAL_AUCTIONS)}
<p>The government's own overview is at {ext("https://www.usa.gov/auctions-and-sales", "USA.gov: government auctions of seized and surplus property")}.</p>

<h2>How federal auctions work</h2>
<ol>
<li><strong>Register</strong> on the auction site. Registration is free.</li>
<li><strong>Read the lot description and terms.</strong> They say where the item is, when you can inspect it, how to pay, and how long you have to remove it.</li>
<li><strong>Inspect if you can.</strong> Items are sold as-is, and descriptions are not guarantees.</li>
<li><strong>Bid.</strong> Sales may be online, in person, or by mail-in bid. Some are run by the agency and some by an auction company under contract.</li>
<li><strong>Pay and pick up on time.</strong> You arrange and pay for removal. Missing the deadline can cost you the item and your right to bid again.</li>
</ol>

<h2>What to check before you bid</h2>
{RISKS}

<h2>Surplus that is not sold to the public</h2>
<p>Before federal surplus reaches public auction, it is first offered to other federal agencies, then to state and local governments and eligible nonprofits through each state's surplus agency. If you run a nonprofit, see <a href="/{DIR}/surplus-property-for-nonprofits.html">surplus property for nonprofits</a>.</p>

<h2>State and local sales</h2>
<p>States, counties, and cities run their own sales. Choose your state: <a href="/{DIR}/">government auctions by state</a>.</p>
{G.faq_html(faq)}
{guides_list("federal-surplus-auctions.html")}
'''
    return dict(title="Federal Government Surplus Auctions: Official Sites | NFCcop",
                description="Where the federal government sells surplus and seized property: GSA Auctions, Treasury auctions, and the U.S. Marshals Service. How bidding works and what to check first.",
                h1="Federal Government Surplus and Seized Property Auctions", body=body, faq=faq)


def guide_federal_real_estate(hubs):
    faq = [
        ("Where can I find government-owned homes for sale?",
         "HUD lists homes on the HUD Home Store, USDA lists rural homes and farms on its resales site, Fannie Mae lists homes on HomePath, and the FDIC lists real estate from failed banks. GSA auctions surplus federal buildings and land."),
        ("Are government homes cheaper?",
         "Not automatically. They are priced or auctioned near market value and sold as-is. The savings, if any, come from condition and from buyers who can handle repairs."),
        ("Can I buy federal land?",
         "Sometimes. The Bureau of Land Management occasionally sells parcels of undeveloped public land, mostly in western states, and GSA sells surplus federal real estate. There is no program that gives away free federal land."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Federal agencies sell real estate on their own sites: HUD for FHA foreclosures, USDA for rural homes and farms, Fannie Mae for its foreclosed homes, the FDIC for failed-bank property, and GSA for surplus federal buildings and land. Each can be searched by state, for free.</p>
</div>
<p>The federal government ends up owning real estate through loan foreclosures, bank failures, forfeiture, and buildings it no longer needs. This page lists the official places to look and how each one sells.</p>
{SCAM}
<h2>Official federal real estate sites</h2>
{fed_table(FEDERAL_REAL_ESTATE)}
<p>Seized real estate is also sold through {ext("https://home.treasury.gov/services/treasury-auctions", "U.S. Treasury auctions")} and the {ext("https://www.usmarshals.gov/what-we-do/asset-forfeiture", "U.S. Marshals Service")}. The government's own overview is at {ext("https://www.usa.gov/real-estate-sales", "USA.gov: real estate and federal lands for sale")}.</p>

<h2>How these sales differ</h2>
<ul>
<li><strong>HUD homes</strong> are sold by bid through a real estate agent registered with HUD. Buyers who will live in the home usually get a first bidding period before investors.</li>
<li><strong>USDA properties</strong> are sold by auction or offer, depending on the property.</li>
<li><strong>Fannie Mae and FDIC properties</strong> are listed with local real estate agents like other homes.</li>
<li><strong>GSA real estate</strong> is sold by online auction, with a registration deposit and set bidding dates.</li>
<li><strong>Federal land</strong> from the Bureau of Land Management is sold only when a specific parcel is identified for sale, by competitive bid at no less than appraised value.</li>
</ul>

<h2>Before you make an offer</h2>
{RISKS}
<p>You can use a mortgage on many of these homes, but a house in poor condition may not qualify for a standard loan. Ask a lender early. Also see <a href="/moving-on/foreclosed-reo-property-research/">researching foreclosed and bank-owned property</a>, <a href="/moving-on/hazard-and-flood-research/">hazard and flood research</a>, and the <a href="/moving-on/foreclosure-research-scam-guide/">foreclosure scam guide</a>.</p>

<h2>State and local real estate sales</h2>
<p>Tax sales, sheriff's sales, and land bank sales are local. Choose your state: <a href="/{DIR}/">government auctions by state</a>. For how tax sales work, see <a href="/{DIR}/tax-sales-explained.html">tax lien and tax deed sales explained</a>.</p>
{G.faq_html(faq)}
{guides_list("federal-real-estate-for-sale.html")}
'''
    return dict(title="Federal Real Estate for Sale: HUD, USDA, GSA, FDIC | NFCcop",
                description="Official places to find government-owned real estate: HUD homes, USDA rural properties, Fannie Mae HomePath, FDIC sales, GSA real estate auctions, and federal land sales.",
                h1="Federal Real Estate for Sale: Homes, Buildings, and Land", body=body, faq=faq)


def guide_tax_sales(hubs):
    rows = "\n".join(
        f'<tr><td><a href="/{DIR}/{h["slug"]}.html">{esc(h["name"])}</a></td><td>{esc(KIND_TEXT[TAX[h["slug"]][0]][0].capitalize())}</td><td>{esc(TAX[h["slug"]][1][0].upper() + TAX[h["slug"]][1][1:])}</td></tr>'
        for h in hubs
    )
    faq = [
        ("What is the difference between a tax lien and a tax deed?",
         "A tax lien sale sells the debt: the buyer pays the back taxes and is repaid with interest if the owner redeems. A tax deed sale sells the property itself after the government forecloses. A redeemable sale sells the property but gives the former owner time to buy it back."),
        ("Do I get the house if I buy a tax lien?",
         "Usually not. Most liens are paid off by the owner. Getting the property takes more time, more notices, and often a court case, and the rules are strict."),
        ("Does a tax sale wipe out the mortgage?",
         "It depends on the state and the type of sale. Some claims are cut off and others survive. Check with a title company or a real estate lawyer before you bid, not after."),
        ("What happens to extra money from a tax sale?",
         "If a property sells for more than the taxes and costs owed, the former owner may have a claim to the surplus. Each state has its own process and deadline for claiming it."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> When property taxes go unpaid, the government sells either the <strong>debt</strong> (a tax lien) or the <strong>property</strong> (a tax deed). Some states sell the property but let the former owner buy it back for a time. Which one you are bidding on changes everything about the risk.</p>
</div>
<p>Tax sale lists are public and free, and they attract a lot of expensive courses and paid lists. This page explains the three systems in plain language, who runs the sale in each state, and what can go wrong.</p>
{SCAM}
<h2>The three systems</h2>
<h3>Tax lien sales</h3>
<p>The government sells its claim for the unpaid taxes. The buyer pays the taxes and holds a lien. If the owner pays, the buyer gets the money back with interest or a penalty set by state law. If the owner never pays, the buyer can start the legal steps to take the property, which take time and must be done exactly right.</p>
<h3>Tax deed sales</h3>
<p>The government forecloses first, then sells the property at auction. The buyer gets a deed. The deed is often not a clean title: many buyers need a court case to clear the title before they can get title insurance, borrow against the property, or resell it.</p>
<h3>Redeemable sales</h3>
<p>The buyer gets a deed or a certificate for the property, but the former owner can redeem for a period after the sale by paying the price plus a penalty. Until that period ends, do not spend money improving the property.</p>

<h2>Who runs tax sales in each state</h2>
<p>This table is a starting point, checked {REVIEWED}. States change these laws, and some states use more than one method. The office in the last column is the authority for its own sale.</p>
<div class="table-wrap"><table><tr><th>State</th><th>What is sold</th><th>Who runs the sale</th></tr>
{rows}
</table></div>

<h2>What can go wrong</h2>
{RISKS}
<ul>
<li><strong>Worthless parcels.</strong> Tax sale lists include drainage ditches, strips with no access, and lots that cannot be built on.</li>
<li><strong>Bankruptcy and notice problems.</strong> A sale can be undone if the owner was in bankruptcy or was not given proper notice.</li>
<li><strong>Federal liens.</strong> An IRS lien can give the federal government its own right to redeem after a sale.</li>
</ul>

<h2>If you are the owner</h2>
<p>You usually have the right to pay before the sale and, in many states, to redeem after it. If the sale brings more than you owed, you may be able to claim the surplus. Do not sign anything from a company offering to "recover" money for a share until you have asked the tax office how to claim it yourself. Free help: <a href="/legal-help/free-legal-aid-by-state.html">free legal aid by state</a> and <a href="/money-help/property-tax-reassessment-after-damage.html">property tax reassessment after damage</a>.</p>
{G.faq_html(faq)}
{guides_list("tax-sales-explained.html")}
'''
    return dict(title="Tax Lien vs. Tax Deed Sales: All 50 States | NFCcop",
                description="Tax lien, tax deed, and redeemable tax sales in plain language, with a 50-state table of what is sold and which office runs the sale. Risks to check before you bid.",
                h1="Tax Lien and Tax Deed Sales Explained, State by State", body=body, faq=faq)


def guide_local(hubs):
    faq = [
        ("How do I find city or county surplus auctions near me?",
         "Go to the city or county's own website and search for surplus, auction, or purchasing. The purchasing, fleet, or finance office posts sales, often with a link to an online auction company that runs the bidding."),
        ("What do cities and counties sell?",
         "Retired police cars and trucks, mowers and heavy equipment, office furniture, computers, and unclaimed or forfeited property held by police. Many also sell vacant lots and houses through a land bank or real estate office."),
        ("Are online government auction sites legitimate?",
         "Many governments do use outside auction companies. To be sure a sale is real, reach it through the link on the government's own website instead of through an ad or a search result."),
    ]
    grid = "\n".join(f'<a href="/{DIR}/{h["slug"]}.html">{esc(h["name"])}</a>' for h in hubs)
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Cities, counties, school districts, and police departments sell their own surplus, and each one posts its own sales. Start at the government's website, search for "surplus" or "auction," and follow its link to the bidding site.</p>
</div>
<p>Local governments replace vehicles and equipment on a schedule and sell the old ones to the public. They also sell property that came to them through unpaid taxes, forfeiture, or abandonment. There is no national list, so this page explains who sells what and how to find it.</p>
{SCAM}
<h2>Who sells what</h2>
<div class="table-wrap"><table><tr><th>Seller</th><th>Typical items</th><th>Office to look for</th></tr>
<tr><td>City or county government</td><td>Cars, trucks, mowers, heavy equipment, furniture, computers</td><td>Purchasing, fleet, finance, or general services</td></tr>
<tr><td>Police or sheriff</td><td>Unclaimed, found, and forfeited property; impounded vehicles</td><td>Property and evidence unit, or the sheriff's civil division</td></tr>
<tr><td>County tax office</td><td>Tax-delinquent real estate</td><td>Treasurer, tax collector, or tax claim bureau</td></tr>
<tr><td>Sheriff or court</td><td>Foreclosed real estate and property seized to pay judgments</td><td>Sheriff's sales page, or the court clerk</td></tr>
<tr><td>Land bank or city real estate office</td><td>Vacant lots and houses, side lots for neighbors</td><td>Land bank, community development, or real estate division</td></tr>
<tr><td>School district, college, utility</td><td>Buses, computers, kitchen and shop equipment</td><td>Purchasing or business office</td></tr>
<tr><td>Transit and airport authorities</td><td>Buses, vehicles, lost-and-found property</td><td>Procurement office</td></tr>
</table></div>

<h2>How to find local sales</h2>
<ol>
<li><strong>Find the official website.</strong> Use {ext("https://www.usa.gov/local-governments", "USA.gov's local government directory")} if you are not sure of the address.</li>
<li><strong>Search the site</strong> for "surplus," "auction," "purchasing," "land bank," or "tax sale."</li>
<li><strong>Follow the government's own link</strong> to the auction. Many use an outside online auction company. That is normal.</li>
<li><strong>Read the legal notices.</strong> Sales of real estate are advertised in the local newspaper of record and often on the clerk's or sheriff's page.</li>
<li><strong>Call the office</strong> and ask when the next sale is and how to get on the notice list. It is free.</li>
</ol>

<h2>Buying city-owned lots and land bank property</h2>
<p>Land banks and city real estate offices often care more about what happens to the property than about the price. Expect an application instead of an open auction, a plan and budget for repairs, proof you are current on your own taxes, and deadlines to finish the work. Neighbors can sometimes buy an adjoining vacant lot at low cost.</p>

<h2>Before you bid</h2>
{RISKS}

<h2>Choose a state</h2>
<p>Each state page lists the state surplus office and who runs tax sales there.</p>
<div class="state-grid">
{grid}
</div>
{G.faq_html(faq)}
{guides_list("city-county-surplus-auctions.html")}
'''
    return dict(title="City and County Surplus Auctions: How to Find Them | NFCcop",
                description="How to find city, county, police, and school district surplus auctions, land bank property, and local real estate sales, starting from the government's own website.",
                h1="City and County Surplus Auctions and Local Government Sales", body=body, faq=faq)


def guide_nonprofits(hubs):
    rows = "\n".join(
        f'<tr><td><a href="/{DIR}/{h["slug"]}.html">{esc(h["name"])}</a></td><td>{esc(SASP[h["slug"]][0])}</td><td>{esc(SASP[h["slug"]][1])}</td></tr>'
        for h in hubs
    )
    faq = [
        ("Can a nonprofit get federal surplus property?",
         "Some can. Federal law lets eligible nonprofits, such as those running education or public health programs, programs for older adults, or services for people who are homeless or impoverished, receive federal surplus through their state agency for surplus property. The state agency decides eligibility."),
        ("Is federal surplus free for nonprofits?",
         "The property is donated, but the state agency charges a service fee to cover its costs for handling and transport. The fee is usually well below market value."),
        ("Are there rules after we receive the property?",
         "Yes. The organization generally must put the property into use within one year and keep using it for at least one year. Some items carry longer restrictions. Breaking the rules can mean returning the property or paying for it."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Eligible nonprofits and public agencies can receive federal surplus property through their state agency for surplus property, paying a service charge instead of the market price. Call your state's agency from the list below and ask for the eligibility application.</p>
</div>
<p>Before federal surplus is auctioned to the public, it is offered to state and local governments and to certain nonprofits. The program is called the Federal Surplus Personal Property Donation Program. Each state runs it through one office. Many of those offices also offer the state's own surplus to nonprofits and local governments before selling it to the public.</p>

<h2>Who can qualify</h2>
<ul>
<li>State and local public agencies</li>
<li>Nonprofit education and public health organizations, including programs for people who are homeless or impoverished</li>
<li>Nonprofit and public programs for older adults</li>
<li>Public airports and certain other special categories</li>
</ul>
<p>The state agency makes the eligibility decision. Expect to show your IRS determination letter, describe the program the property will be used for, and name the people allowed to pick up property for you.</p>

<h2>How it works</h2>
<ol>
<li><strong>Call your state agency</strong> and ask for the eligibility application.</li>
<li><strong>Get approved</strong> and receive a donee account.</li>
<li><strong>Look for property.</strong> The agency has a warehouse or online inventory and can search federal listings for items you need.</li>
<li><strong>Pay the service charge</strong> and arrange pickup.</li>
<li><strong>Use it.</strong> Put the property into use within one year and keep using it for at least one year. Keep records.</li>
</ol>

<h2>State agencies for surplus property</h2>
<p>From the U.S. General Services Administration's contact list, checked {REVIEWED}. Current contacts: {ext("https://gsa.gov/sasp", "gsa.gov/sasp")}.</p>
<div class="table-wrap"><table><tr><th>State</th><th>Agency</th><th>Phone</th></tr>
{rows}
</table></div>

<h2>Other ways nonprofits get equipment</h2>
<ul>
<li><strong>State surplus:</strong> ask the same office whether nonprofits can buy state surplus before public sale.</li>
<li><strong>Local governments:</strong> cities, counties, and school districts can often donate or sell surplus to nonprofits directly. Ask the purchasing office.</li>
<li><strong>Public auctions:</strong> nonprofits can bid like anyone else. See <a href="/{DIR}/federal-surplus-auctions.html">federal surplus auctions</a> and <a href="/{DIR}/city-county-surplus-auctions.html">city and county surplus auctions</a>.</li>
</ul>
{G.faq_html(faq)}
{guides_list("surplus-property-for-nonprofits.html")}
'''
    return dict(title="Federal Surplus Property for Nonprofits: State Contacts | NFCcop",
                description="How eligible nonprofits and local governments get federal surplus property through their state agency for surplus property, with the agency and phone number for all 50 states.",
                h1="Surplus Property for Nonprofits and Local Governments", body=body, faq=faq)


GUIDE_BUILDERS = {
    "federal-surplus-auctions.html": guide_federal_surplus,
    "federal-real-estate-for-sale.html": guide_federal_real_estate,
    "tax-sales-explained.html": guide_tax_sales,
    "city-county-surplus-auctions.html": guide_local,
    "surplus-property-for-nonprofits.html": guide_nonprofits,
}


def index_page(hubs):
    grid = "\n".join(f'<a href="/{DIR}/{h["slug"]}.html">{esc(h["name"])}</a>' for h in hubs)
    guides = "".join(f'<li><a href="/{DIR}/{f}">{esc(t)}</a></li>' for f, t in GUIDES)
    faq = [
        ("Where do governments sell surplus property and real estate?",
         "Federal agencies sell on their own sites, such as GSA Auctions and the HUD Home Store. Each state has a surplus property office. Counties and cities run tax sales, sheriff's sales, and their own surplus auctions."),
        ("Do I have to pay to see government auction lists?",
         "No. Official lists are free on government websites. Be careful with sites that charge for access."),
    ]
    body = f'''
<div class="quick-answer">
<p><strong>Short answer:</strong> Governments at every level sell surplus equipment and real estate to the public, and every official list is free. Pick your state for the state surplus office, who runs tax sales, and how to find local and federal sales there.</p>
</div>
{SCAM}
<h2>Choose a state</h2>
<div class="state-grid">
{grid}
</div>
<h2>Guides</h2>
<ul>{guides}</ul>
<h2>The three levels</h2>
<ul>
<li><strong>Federal:</strong> surplus vehicles and equipment, seized property, HUD and USDA homes, surplus federal buildings and land.</li>
<li><strong>State:</strong> state surplus vehicles and equipment, unclaimed property auctions, and state-owned land.</li>
<li><strong>Local:</strong> tax-delinquent real estate, foreclosure and sheriff's sales, city and county surplus, police property, and land bank lots.</li>
</ul>
<h2>Before you bid</h2>
{RISKS}
{G.faq_html(faq)}
'''
    return dict(title="Government Auctions by State: Surplus and Real Estate | NFCcop",
                description="Find government surplus property, tax sales, and real estate auctions in all 50 states, plus official federal auction sites. Every official list is free.",
                h1="Government Auctions by State: Surplus Property and Real Estate", body=body, faq=faq)


def main():
    slugs = sorted(p.stem for p in (ROOT / "states").glob("*.html") if p.stem != "index")
    hubs = [G.load_hub(s) for s in slugs]
    missing = [s for s in slugs if s not in SASP or s not in TAX]
    if missing:
        sys.exit(f"no surplus data for: {missing}")
    paths = []
    for hub in hubs:
        rel = f'{DIR}/{hub["slug"]}.html'
        crumbs = [("Home", "/"), CRUMB, (hub["name"], "")]
        write(rel, shell(url_path=rel, crumbs=crumbs, about=hub["name"], slug=hub["slug"], **state_page(hub)))
        paths.append(rel)
    for fname, title in GUIDES:
        rel = f"{DIR}/{fname}"
        crumbs = [("Home", "/"), CRUMB, (title, "")]
        write(rel, shell(url_path=rel, crumbs=crumbs, **GUIDE_BUILDERS[fname](hubs)))
        paths.append(rel)
    rel = f"{DIR}/index.html"
    write(rel, shell(url_path=f"{DIR}/", crumbs=[("Home", "/"), ("Government auctions", "")], **index_page(hubs)))
    paths.append(f"{DIR}/")

    touched = 0
    for hub in hubs:
        slug, name = hub["slug"], hub["name"]
        block = f'<p><strong>Buying from the government in {esc(name)}:</strong> <a href="/{DIR}/{slug}.html">{esc(name)} surplus property, tax sales, and real estate auctions</a>.</p>'
        touched += G.inject(f"states/{slug}.html", "state-auction-link", block, '<section id="reader-questions"')
    block = f'<h2>Government auctions</h2>\n<ul><li><a href="/{DIR}/">Government surplus, tax sales, and real estate auctions by state</a></li></ul>'
    touched += G.inject("states/index.html", "state-auction-index", block, "<!-- state-resource-index -->")
    touched += G.inject("moving-on/index.html", "state-auction-index", block, "<h2>Watch for scams and unsafe shortcuts</h2>")
    added = G.update_sitemap(paths)
    print(f"wrote {len(paths)} pages; linked from {touched} existing pages; added {added} sitemap entries; state surplus links: {len(STATE_LINKS)}")


if __name__ == "__main__":
    main()
