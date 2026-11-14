"""Data for the government-auctions series (built by build_surplus_pages.py).

SASP: each state's agency for surplus property and its phone number, copied
from the GSA contact list at https://gsa.gov/sasp on 2026-11-14. Agency names
are lightly edited so they read with the state name.

TAX: how tax-delinquent real estate is sold in each state, in plain words.
kind is one of lien / deed / redeemable / mixed. `who` is the office that
runs the sale. Redemption periods, interest rates and sale dates are left out
on purpose: they change, and the county office is the authority.
Louisiana changed to tax lien auctions on 2026-01-01 (2024 Act 774).
"""

SASP = {
    "alabama": ("ADECA Surplus Property", "334-284-0577"),
    "alaska": ("Alaska Division of General Services, Property Management Office", "907-754-3405"),
    "arizona": ("Arizona State Surplus Property Management", "602-542-5701"),
    "arkansas": ("Arkansas Federal Surplus Property", "501-835-3111"),
    "california": ("California Department of General Services", "916-327-0535"),
    "colorado": ("Colorado State Agency for Surplus Property", "720-661-3647"),
    "connecticut": ("Connecticut Department of Administrative Services", "860-713-5052"),
    "delaware": ("Delaware Surplus Services", "302-836-7640"),
    "florida": ("Florida Department of Management Services, Federal Property Assistance", "904-964-5601"),
    "georgia": ("Georgia Department of Administrative Services, Surplus Property Division", "404-657-8544"),
    "hawaii": ("Hawaii State Agency for Surplus Property", "808-831-6757"),
    "idaho": ("Idaho Federal Surplus Property", "208-334-3477"),
    "illinois": ("Illinois Department of Central Management Services, Federal Surplus Division", "217-785-6903"),
    "indiana": ("Indiana Department of Administration, Federal Surplus Property", "317-234-3690"),
    "iowa": ("Iowa Federal Surplus Property", "515-266-6913"),
    "kansas": ("Kansas Federal Surplus Property", "785-296-2351"),
    "kentucky": ("Kentucky Division of Surplus Property", "502-573-4836"),
    "louisiana": ("Louisiana Federal Property Assistance", "225-342-7860"),
    "maine": ("Maine federal surplus donation program", "207-287-4593"),
    "maryland": ("Maryland State Agency for Surplus Property", "410-767-1171"),
    "massachusetts": ("Massachusetts State Agency for Surplus Property", "617-720-3170"),
    "michigan": ("Michigan State and Federal Surplus", "517-241-1916"),
    "minnesota": ("Minnesota Surplus Services", "651-201-2510"),
    "mississippi": ("Mississippi Office of Surplus Property", "601-939-2050"),
    "missouri": ("Missouri State Agency for Surplus Property", "573-751-3415"),
    "montana": ("Montana State Agency for Surplus Property", "406-444-9921"),
    "nebraska": ("Nebraska Federal Surplus Property", "402-471-2677"),
    "nevada": ("Nevada State Surplus Property Program", "775-684-0192"),
    "new-hampshire": ("New Hampshire Federal Surplus Property Program", "603-271-7412"),
    "new-jersey": ("New Jersey State Police (federal surplus program)", "609-963-6900"),
    "new-mexico": ("New Mexico State Agency for Surplus Property", "505-476-1949"),
    "new-york": ("New York Bureau of Federal Property Assistance", "518-485-8222"),
    "north-carolina": ("North Carolina Federal Surplus Property Agency", "919-814-5614"),
    "north-dakota": ("North Dakota Surplus Property", "701-328-9667"),
    "ohio": ("Ohio Federal Surplus Property Program", "614-949-2863"),
    "oklahoma": ("Oklahoma Property Reutilization Division, State and Federal Surplus", "405-425-2700"),
    "oregon": ("Oregon Department of Administrative Services", "503-378-6057"),
    "pennsylvania": ("Pennsylvania Federal Surplus and Law Enforcement Property Division", "717-787-9724"),
    "rhode-island": ("Rhode Island State Agency for Surplus Property", "401-462-3101"),
    "south-carolina": ("South Carolina Surplus Property Office", "803-896-6880"),
    "south-dakota": ("South Dakota Federal Property Agency", "605-353-7150"),
    "tennessee": ("Tennessee Department of General Services, Vehicles and Asset Management", "615-350-3373"),
    "texas": ("Texas State and Federal Surplus Property Program", "512-507-7643"),
    "utah": ("Utah State Agency for Surplus Property", "801-619-7219"),
    "vermont": ("Vermont Surplus", "802-241-3384"),
    "virginia": ("Virginia Federal Surplus Office", "276-228-6803"),
    "washington": ("Washington Department of Enterprise Services, Surplus Operations", "360-407-1926"),
    "west-virginia": ("West Virginia Purchasing Division", "304-356-2425"),
    "wisconsin": ("Wisconsin Department of Administration, State Bureau of Procurement", "608-266-5462"),
    "wyoming": ("Wyoming Surplus Property, Department of Administration and Information", "307-777-7901"),
}

TAX = {
    "alabama": ("mixed", "the county tax collector or revenue commissioner", "Counties may hold a tax lien auction or an older-style tax sale. Property that does not sell goes to the state, and the Alabama Department of Revenue sells state-held tax-delinquent land."),
    "alaska": ("deed", "the borough or city", "Alaska has no counties. Boroughs and cities foreclose on unpaid taxes and later sell the property. The state Department of Natural Resources also holds separate state land sales."),
    "arizona": ("lien", "the county treasurer", ""),
    "arkansas": ("deed", "the Commissioner of State Lands", "Arkansas is unusual: counties send tax-delinquent land to a state office, the Commissioner of State Lands, which holds the public auctions county by county."),
    "california": ("deed", "the county tax collector", ""),
    "colorado": ("lien", "the county treasurer", ""),
    "connecticut": ("redeemable", "the town or city tax collector", "Connecticut has no county government. Tax sales are run by each town or city."),
    "delaware": ("redeemable", "the county, usually through a sheriff's sale", ""),
    "florida": ("mixed", "the county tax collector (tax certificates) and the clerk of the circuit court (tax deed sales)", "Florida has two steps. The tax collector first sells tax certificates, which are liens. If a certificate is not paid off, the holder can apply for a tax deed, and the clerk of court then auctions the property itself."),
    "georgia": ("redeemable", "the county tax commissioner, often through a sheriff's tax sale", ""),
    "hawaii": ("redeemable", "the county real property tax office", ""),
    "idaho": ("deed", "the county treasurer and county commissioners", ""),
    "illinois": ("lien", "the county treasurer", ""),
    "indiana": ("lien", "the county treasurer and county auditor", "Indiana buyers receive a tax sale certificate. Liens that do not sell may be offered again at a county commissioners' certificate sale."),
    "iowa": ("lien", "the county treasurer", ""),
    "kansas": ("deed", "the county, through a court foreclosure and a sheriff's or county auction", ""),
    "kentucky": ("lien", "the county clerk", "Kentucky sells certificates of delinquency. Buyers generally must register with the state Department of Revenue first."),
    "louisiana": ("lien", "the parish tax collector, usually the sheriff", "Louisiana switched to tax lien auctions on January 1, 2026. Before that, buyers received a tax sale title. Parishes also sell older adjudicated property under the earlier rules."),
    "maine": ("deed", "the town or city", "Maine towns take title through an automatic tax lien foreclosure and then sell the property. Maine Revenue Services sells tax-acquired property in the unorganized territory."),
    "maryland": ("lien", "the county collector, or Baltimore City", ""),
    "massachusetts": ("mixed", "the city or town treasurer or collector", "Massachusetts cities and towns take a tax title, foreclose in Land Court, and then auction the property. Some also assign tax titles to buyers."),
    "michigan": ("deed", "the county treasurer, or the state for some counties", "Michigan forecloses once a year and sells the properties at public auctions, most of them online."),
    "minnesota": ("deed", "the county auditor or auditor-treasurer", "Minnesota calls this tax-forfeited land. Counties sell it at public auction."),
    "mississippi": ("lien", "the county tax collector", "Parcels that do not sell go to the state, and the Mississippi Secretary of State sells tax-forfeited land."),
    "missouri": ("lien", "the county collector", ""),
    "montana": ("lien", "the county treasurer", ""),
    "nebraska": ("lien", "the county treasurer", ""),
    "nevada": ("deed", "the county treasurer", ""),
    "new-hampshire": ("deed", "the town or city tax collector", "New Hampshire towns take a tax deed and then decide how to sell the property."),
    "new-jersey": ("lien", "the municipal tax collector", "Tax sales in New Jersey are run by each municipality, not the county."),
    "new-mexico": ("deed", "the Property Tax Division of the state Taxation and Revenue Department", "New Mexico is unusual: a state office, not the county, auctions tax-delinquent property, one county at a time."),
    "new-york": ("mixed", "the county or city", "Most New York counties foreclose and auction the property itself. New York City has used tax lien sales instead."),
    "north-carolina": ("deed", "the county or city tax office, through a court foreclosure", "North Carolina foreclosure sales stay open for upset bids after the auction, so the first high bid is not always the last."),
    "north-dakota": ("deed", "the county auditor", ""),
    "ohio": ("mixed", "the county sheriff, treasurer, and auditor", "Ohio sells tax-foreclosed property at sheriff's sales. Larger counties may also sell tax lien certificates, and many counties have a land bank. Parcels that do not sell can be offered again at an auditor's forfeited land sale."),
    "oklahoma": ("deed", "the county treasurer", ""),
    "oregon": ("deed", "the county", ""),
    "pennsylvania": ("deed", "the county tax claim bureau", "Pennsylvania has three stages: an upset sale, a judicial sale, and a repository of unsold property. Philadelphia and Allegheny County use sheriff's sales."),
    "rhode-island": ("redeemable", "the city or town tax collector", ""),
    "south-carolina": ("redeemable", "the county delinquent tax collector or treasurer", ""),
    "south-dakota": ("lien", "the county treasurer", "Some South Dakota counties no longer sell tax certificates to the public. Ask the county treasurer."),
    "tennessee": ("redeemable", "the county, through a court case, with the sale held by the clerk and master", ""),
    "texas": ("redeemable", "the county sheriff or constable", ""),
    "utah": ("deed", "the county auditor", ""),
    "vermont": ("redeemable", "the town tax collector", "Vermont tax sales are run by each town."),
    "virginia": ("deed", "the county or city treasurer, through a court-ordered sale", ""),
    "washington": ("deed", "the county treasurer", ""),
    "west-virginia": ("lien", "the State Auditor's Office", "West Virginia moved these sales from county sheriffs to the State Auditor's Office under a law passed in 2022. The Auditor's office holds the auctions county by county."),
    "wisconsin": ("deed", "the county treasurer", ""),
    "wyoming": ("lien", "the county treasurer", ""),
}

KIND_TEXT = {
    "lien": ("tax lien", "{name} sells tax liens. The winning bidder pays the back taxes and gets a lien on the property, not the property itself. The owner can pay the bidder back with interest. Only if the owner does not, and the bidder completes more legal steps, can the bidder end up with the property."),
    "deed": ("tax deed", "{name} sells the property itself, not a lien. The government first forecloses on the unpaid taxes and then sells the property, usually at public auction to the highest bidder."),
    "redeemable": ("redeemable tax sale", "{name} sells the property, but the former owner has a set time after the sale to buy it back by paying the bidder the price plus a penalty. Until that time runs out, the buyer does not have full, secure ownership."),
    "mixed": ("more than one kind of tax sale", "{name} uses more than one method, depending on the county or the stage of the process. Read the notice for the specific sale to see whether a lien or the property itself is being sold."),
}

# Shown on every state page and on the federal guides. URLs taken from USA.gov's
# "Real estate and federal lands for sale by the government" page, 2026-11-14.
FEDERAL_REAL_ESTATE = [
    ("HUD Home Store", "https://www.hudhomestore.gov/Home/Index.aspx", "U.S. Department of Housing and Urban Development", "Homes HUD took back after FHA loan foreclosures. Search by state. Bids go through a registered real estate agent."),
    ("USDA real estate for sale", "https://properties.sc.egov.usda.gov/resales/public/home", "U.S. Department of Agriculture", "Rural homes, farms, and ranches from USDA loan programs, sold by auction or offer."),
    ("Fannie Mae HomePath", "https://homepath.fanniemae.com/", "Fannie Mae", "Foreclosed single-family homes owned by Fannie Mae."),
    ("FDIC real estate sales", "https://www.fdic.gov/buying/owned/", "Federal Deposit Insurance Corporation", "Homes and commercial real estate from failed banks."),
    ("GSA real estate sales", "https://realestatesales.gov/", "U.S. General Services Administration", "Surplus federal buildings and land, sold by online auction."),
    ("Bureau of Land Management land sales", "https://www.blm.gov/programs/lands-and-realty/sales-and-exchanges", "U.S. Department of the Interior", "Occasional sales of undeveloped public land, mostly in western states."),
]
FEDERAL_AUCTIONS = [
    ("GSA Auctions", "https://gsaauctions.gov/", "U.S. General Services Administration", "Federal surplus vehicles, equipment, furniture, and electronics. Search by state."),
    ("U.S. Treasury auctions", "https://home.treasury.gov/services/treasury-auctions", "U.S. Department of the Treasury", "Property forfeited for violations of Treasury law, including real estate, vehicles, and other goods."),
    ("U.S. Marshals Service asset forfeiture", "https://www.usmarshals.gov/what-we-do/asset-forfeiture", "U.S. Department of Justice", "Seized homes, land, vehicles, and other property, sold through contractors the Marshals Service lists."),
]
