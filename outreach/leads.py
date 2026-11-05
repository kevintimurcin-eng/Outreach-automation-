"""Lead storage: a plain CSV file that you can open in Excel or Google Sheets."""
from __future__ import annotations

import csv
import re
from pathlib import Path

FIELDS = ["email", "first_name", "last_name", "position", "company", "domain",
          "city", "segment", "source", "notes"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def read_leads(path: str | Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [{k: (row.get(k) or "").strip() for k in FIELDS} for row in csv.DictReader(f)]


def write_leads(path: str | Path, leads: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for lead in leads:
            w.writerow({k: lead.get(k, "") for k in FIELDS})


def read_suppression(path: str | Path) -> set[str]:
    return {l["email"].lower() for l in read_leads(path) if l["email"]}


def merge(existing: list[dict], new: list[dict]) -> list[dict]:
    """Add new leads, de-duplicating by email (or by domain for company-only rows)."""
    def key(l):
        return ("e", l["email"].lower()) if l.get("email") else ("d", l.get("domain", "").lower(), l.get("company", "").lower())
    seen = {key(l): l for l in existing}
    for lead in new:
        lead = {k: (lead.get(k) or "").strip() for k in FIELDS}
        k = key(lead)
        if k in seen:
            for f in FIELDS:  # fill in blanks only, never overwrite your edits
                if not seen[k].get(f):
                    seen[k][f] = lead[f]
        else:
            seen[k] = lead
    return list(seen.values())


def sendable(leads: list[dict], suppressed: set[str]) -> list[dict]:
    out, seen = [], set()
    for l in leads:
        e = l["email"].lower()
        if is_valid_email(e) and e not in suppressed and e not in seen:
            seen.add(e)
            out.append(l)
    return out
