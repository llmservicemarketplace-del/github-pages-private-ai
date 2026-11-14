"""Per-state facts for the state resource series (built by build_state_resource_pages.py).

Agency names, links and phone numbers are NOT stored here: the builder reads
them from the already-verified directory table on each states/{slug}.html hub,
so there is one source of truth. This file holds only what the hubs do not
carry in structured form.

SMALL: (court that hears small claims, dollar limit, note). Limits were checked
on 2026-11-14 against state court or legislature sources. Recent changes:
  Arizona  $5,000   (2025 SB 1022, up from $3,500)
  Idaho    $15,000  (2026 S 1330, effective July 1, 2026, up from $5,000)
  Kansas   $10,000  (2024 HB 2604, up from $4,000)
  Maine    $10,000  (PL 2025 c. 261, effective Jan 1, 2026, up from $6,000)
  Minnesota $20,000 (Minn. Stat. 491A.01; $4,000 consumer credit)
  West Virginia $20,000 (2025 HB 2761, effective July 7, 2025, up from $10,000)
  Utah     $20,000  (Utah Code 78A-8-102 schedule, 2025 through 2029)
"""

SMALL = {
    "alabama": ("the small claims division of District Court", "$6,000", ""),
    "alaska": ("District Court", "$10,000", ""),
    "arizona": ("the small claims division of Justice Court", "$5,000", "A 2025 law raised the limit from $3,500. Some county court pages still show the old figure, so confirm with the justice court."),
    "arkansas": ("the small claims division of District Court", "$5,000", ""),
    "california": ("the small claims division of Superior Court", "$12,500 for individuals ($6,250 for most businesses)", ""),
    "colorado": ("the small claims division of County Court", "$7,500", ""),
    "connecticut": ("the small claims session of Superior Court", "$5,000", ""),
    "delaware": ("Justice of the Peace Court", "$25,000", "Delaware has no separate small claims court. The Justice of the Peace Court is where people file smaller civil claims without a lawyer."),
    "florida": ("County Court", "$8,000", ""),
    "georgia": ("Magistrate Court", "$15,000", "Georgia has no court named \"small claims.\" Magistrate Court fills that role."),
    "hawaii": ("the small claims division of District Court", "$5,000", ""),
    "idaho": ("the small claims department of the magistrate division of District Court", "$15,000", "The limit rose from $5,000 to $15,000 on July 1, 2026. Older guides and forms may still show $5,000."),
    "illinois": ("Circuit Court", "$10,000", ""),
    "indiana": ("the small claims docket of your county's circuit, superior, or city or town court", "$10,000", ""),
    "iowa": ("District Court (small claims docket)", "$6,500", ""),
    "kansas": ("District Court", "$10,000", "A 2024 law raised the limit from $4,000. Older guides may still show $4,000."),
    "kentucky": ("the small claims division of District Court", "$2,500", ""),
    "louisiana": ("the small claims division of City Court, or a Justice of the Peace Court", "$5,000", "Louisiana uses parishes instead of counties, and which court you use depends on where you live."),
    "maine": ("District Court", "$10,000", "The limit rose from $6,000 to $10,000 on January 1, 2026."),
    "maryland": ("District Court", "$5,000", ""),
    "massachusetts": ("District Court, Boston Municipal Court, or Housing Court", "$7,000", ""),
    "michigan": ("the small claims division of District Court", "$7,000", ""),
    "minnesota": ("Conciliation Court", "$20,000 ($4,000 if the claim involves a consumer credit transaction)", "Minnesota calls small claims court Conciliation Court."),
    "mississippi": ("Justice Court", "$3,500", ""),
    "missouri": ("the small claims division of Circuit Court", "$5,000", ""),
    "montana": ("the small claims division of Justice Court", "$7,000", ""),
    "nebraska": ("County Court", "$7,500", "Nebraska adjusts this limit every five years. Confirm the current figure with the Judicial Branch."),
    "nevada": ("Justice Court", "$10,000", ""),
    "new-hampshire": ("the District Division of Circuit Court", "$10,000", ""),
    "new-jersey": ("the Small Claims Section of the Superior Court's Special Civil Part", "$5,000", "Claims up to $20,000 can go to the regular Special Civil Part."),
    "new-mexico": ("Magistrate Court (Metropolitan Court in Bernalillo County)", "$10,000", ""),
    "new-york": ("the small claims part of your city, town, or village court", "$10,000 in New York City, $5,000 in city courts outside New York City, and $3,000 in town and village courts", ""),
    "north-carolina": ("the small claims division of District Court, before a magistrate", "$10,000", ""),
    "north-dakota": ("District Court (small claims)", "$15,000", ""),
    "ohio": ("the small claims division of your municipal or county court", "$6,000", ""),
    "oklahoma": ("District Court (small claims docket)", "$10,000", ""),
    "oregon": ("the small claims department of Circuit Court", "$10,000", ""),
    "pennsylvania": ("Magisterial District Court", "$12,000", "Pennsylvania has no court named \"small claims.\" A magisterial district judge hears these cases."),
    "rhode-island": ("District Court", "$5,000", ""),
    "south-carolina": ("Magistrate Court", "$7,500", ""),
    "south-dakota": ("small claims court, held by the magistrate court in your county", "$12,000", ""),
    "tennessee": ("General Sessions Court", "$25,000", "Tennessee has no court named \"small claims.\" General Sessions Court fills that role."),
    "texas": ("Justice Court (justice of the peace court)", "$20,000", ""),
    "utah": ("the small claims department of Justice Court or District Court", "$20,000", "Utah law sets the limit on a schedule: $20,000 from 2025 through 2029. Confirm the current figure on the court's small claims page."),
    "vermont": ("the civil division of Superior Court (small claims docket)", "$10,000", ""),
    "virginia": ("the small claims division of General District Court", "$5,000", ""),
    "washington": ("the small claims department of District Court", "$10,000 for individuals", ""),
    "west-virginia": ("Magistrate Court", "$20,000", "West Virginia has no court named \"small claims.\" The limit for Magistrate Court rose from $10,000 to $20,000 in July 2025."),
    "wisconsin": ("Circuit Court (small claims)", "$10,000", "Some injury claims have a lower limit. The clerk of circuit court can confirm which limit applies."),
    "wyoming": ("Circuit Court", "$6,000", ""),
}

# What the state calls SNAP, when it is not just "SNAP".
SNAP_NAME = {
    "arizona": "Nutrition Assistance",
    "california": "CalFresh",
    "michigan": "the Food Assistance Program",
    "north-carolina": "Food and Nutrition Services (FNS)",
    "vermont": "3SquaresVT",
    "washington": "Basic Food",
    "wisconsin": "FoodShare",
}

# What the state calls Medicaid, when it has its own name.
MEDICAID_NAME = {
    "arizona": "AHCCCS",
    "california": "Medi-Cal",
    "colorado": "Health First Colorado",
    "connecticut": "HUSKY Health",
    "hawaii": "Med-QUEST",
    "kansas": "KanCare",
    "maine": "MaineCare",
    "massachusetts": "MassHealth",
    "minnesota": "Medical Assistance",
    "missouri": "MO HealthNet",
    "new-jersey": "NJ FamilyCare",
    "oklahoma": "SoonerCare",
    "oregon": "the Oregon Health Plan (OHP)",
    "pennsylvania": "Medical Assistance",
    "south-carolina": "Healthy Connections",
    "tennessee": "TennCare",
    "washington": "Apple Health",
    "wisconsin": "BadgerCare Plus",
}

# States that have NOT adopted the ACA Medicaid expansion (KFF tracker, August 2026).
NOT_EXPANDED = {
    "alabama", "florida", "georgia", "kansas", "mississippi",
    "south-carolina", "tennessee", "texas", "wisconsin", "wyoming",
}

# What the state calls its LIHEAP energy program, when it has its own name.
ENERGY_NAME = {
    "alaska": "the Heating Assistance Program",
    "colorado": "LEAP",
    "connecticut": "the Connecticut Energy Assistance Program (CEAP)",
    "indiana": "the Energy Assistance Program (EAP)",
    "kansas": "LIEAP",
    "maine": "HEAP",
    "massachusetts": "fuel assistance",
    "new-hampshire": "the Fuel Assistance Program",
    "new-york": "HEAP",
    "ohio": "HEAP",
    "utah": "HEAT",
    "vermont": "fuel assistance",
    "west-virginia": "LIEAP",
    "wisconsin": "WHEAP",
    "wyoming": "LIEAP",
}
