#!/usr/bin/env python3
"""Provider selection and hard spend ceilings. Planning only; never charges an API."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class Provider:
    name: str
    category: str
    auth: str
    monthly_min_usd: Decimal
    quality: int
    status: str

PROVIDERS=(
    Provider("apple_itunes","apps","none",Decimal("0"),3,"implemented"),
    Provider("apple_reviews","reviews","none",Decimal("0"),3,"implemented"),
    Provider("hackernews","community","none",Decimal("0"),2,"implemented"),
    Provider("reddit_oauth","community","oauth",Decimal("0"),3,"credential_gated"),
    Provider("google_trends_alpha","trends","approved_access",Decimal("0"),4,"not_integrated"),
    Provider("serpapi_free","search_trends","api_key",Decimal("0"),4,"credential_gated"),
    Provider("serpapi_starter","search_trends","api_key",Decimal("25"),4,"not_integrated"),
    Provider("dataforseo","seo_keywords_apps","api_key",Decimal("50"),4,"not_integrated"),
    Provider("google_search_console","first_party_seo","oauth",Decimal("0"),5,"not_integrated"),
    Provider("google_analytics","first_party_conversion","oauth",Decimal("0"),5,"not_integrated"),
    Provider("youtube_data","creator_trends","api_key",Decimal("0"),3,"not_integrated"),
    Provider("github_public","developer_trends","token_optional",Decimal("0"),3,"not_integrated"),
)
def select(max_upfront_usd="0",allowed=None):
    ceiling=Decimal(str(max_upfront_usd))
    if ceiling<0:raise ValueError("negative budget")
    allowed=set(allowed or ())
    return [{"provider":p.name,"category":p.category,"status":p.status,
             "upfront_usd":str(p.monthly_min_usd),
             "eligible":p.monthly_min_usd<=ceiling,
             "requires_approval":p.monthly_min_usd>0 or p.auth!="none",
             "enabled":p.status=="implemented" and p.auth=="none",
             "note":"Eligibility is NOT purchase authorization or proof of live API access"}
            for p in PROVIDERS if not allowed or p.name in allowed]
