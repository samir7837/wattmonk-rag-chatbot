def classify_query(query: str) -> str:
    """
    Classify user query into:
    - GENERAL
    - NEC
    - WATTMONK
    """

    q = query.lower().strip()

    nec_keywords = [
        "nec",
        "electrical code",
        "article 690",
        "article 250",
        "article 705",
        "pv system",
        "photovoltaic",
        "grounding",
        "bonding",
        "disconnect",
        "electrical installation",
        "solar code",
        "code requirement",
        "wire sizing",
        "overcurrent",
        "conductor",
        "branch circuit",
        "panelboard",
        "service equipment",
        "rapid shutdown",
        "interconnection code"
    ]

    wattmonk_keywords = [
        "wattmonk",
        "company",
        "services",
        "founder",
        "proposal",
        "planset",
        "plan set",
        "pto",
        "interconnection",
        "site survey",
        "solar store",
        "sales proposal",
        "engineering review",
        "permit",
        "permit package",
        "zippy",
        "ahj",
        "utility provider"
    ]

    if any(keyword in q for keyword in nec_keywords):
        return "NEC"

    if any(keyword in q for keyword in wattmonk_keywords):
        return "WATTMONK"

    return "GENERAL"