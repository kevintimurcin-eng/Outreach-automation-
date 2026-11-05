"""Find published business email addresses for a company domain with Hunter.io."""
from __future__ import annotations

import os

import requests

URL = "https://api.hunter.io/v2/domain-search"

# Roles most likely to commission architecture work.
DEFAULT_DEPARTMENTS = "executive,management,operations"


def find_emails(domain: str, limit: int = 5, departments: str = DEFAULT_DEPARTMENTS,
                min_confidence: int = 80, session: requests.Session | None = None) -> list[dict]:
    s = session or requests.Session()
    r = s.get(URL, params={"domain": domain, "limit": limit, "type": "personal",
                           "department": departments},
              headers={"X-API-KEY": os.environ.get("HUNTER_API_KEY", "placeholder")},
              timeout=30)
    r.raise_for_status()
    data = r.json().get("data", {})
    out = []
    for e in data.get("emails", []):
        if (e.get("confidence") or 0) < min_confidence:
            continue
        out.append({
            "email": e.get("value", ""),
            "first_name": e.get("first_name") or "",
            "last_name": e.get("last_name") or "",
            "position": e.get("position") or "",
            "company": data.get("organization") or "",
            "domain": domain,
            "source": "hunter",
        })
    return out
