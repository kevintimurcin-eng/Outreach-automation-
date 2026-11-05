"""Find companies (developers, hotels, property managers...) with Google Places API (New)."""
from __future__ import annotations

import os
from urllib.parse import urlparse

import requests

URL = "https://places.googleapis.com/v1/places:searchText"


def domain_of(url: str) -> str:
    host = urlparse(url if "//" in url else "//" + url).hostname or ""
    return host.removeprefix("www.").lower()


def search_companies(query: str, segment: str = "", max_results: int = 20,
                     session: requests.Session | None = None) -> list[dict]:
    s = session or requests.Session()
    headers = {
        # In Claude cloud sessions the proxy injects the real key into this header.
        "X-Goog-Api-Key": os.environ.get("GOOGLE_PLACES_API_KEY", "placeholder"),
        "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.formattedAddress,nextPageToken",
    }
    leads, token = [], None
    while len(leads) < max_results:
        body = {"textQuery": query, "pageSize": min(20, max_results - len(leads))}
        if token:
            body["pageToken"] = token
        r = s.post(URL, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        for p in data.get("places", []):
            site = p.get("websiteUri", "")
            leads.append({
                "company": p.get("displayName", {}).get("text", ""),
                "domain": domain_of(site) if site else "",
                "city": p.get("formattedAddress", ""),
                "segment": segment,
                "source": f"google_places:{query}",
            })
        token = data.get("nextPageToken")
        if not token:
            break
    return leads
