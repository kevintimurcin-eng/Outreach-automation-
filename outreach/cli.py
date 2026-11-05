"""Command line entry point:  python -m outreach <command> ..."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import leads as L
from .render import ROOT, build_message, load_config, render
from .send import send_outbox, write_outbox

DEFAULT_LEADS = ROOT / "data" / "leads.csv"
DEFAULT_SUPPRESS = ROOT / "data" / "suppression.csv"


def cmd_import(a):
    merged = L.merge(L.read_leads(a.leads), L.read_leads(a.csv))
    L.write_leads(a.leads, merged)
    print(f"{len(merged)} rows in {a.leads}")


def _ready(a):
    rows = L.read_leads(a.leads)
    if a.segment:
        rows = [r for r in rows if r["segment"] == a.segment]
    return L.sendable(rows, L.read_suppression(a.suppress))


def cmd_preview(a):
    cfg = load_config(a.config)
    ready = _ready(a)
    if not ready:
        sys.exit("No sendable leads (need a valid email, not on the suppression list).")
    subject, body = render(a.template, ready[0], cfg)
    print(f"To: {ready[0]['email']}\nSubject: {subject}\n\n{body}")
    print(f"--- {len(ready)} lead(s) ready for template {a.template!r}")


def cmd_render(a):
    cfg = load_config(a.config)
    msgs = []
    for lead in _ready(a):
        subject, body = render(a.template, lead, cfg)
        msgs.append(build_message(lead, subject, body, cfg))
    paths = write_outbox(msgs, Path(a.outbox))
    print(f"Wrote {len(paths)} emails to {a.outbox}/ – review them before sending.")


def cmd_send(a):
    for line in send_outbox(Path(a.outbox), limit=a.limit, dry_run=not a.confirm):
        print(line)
    if not a.confirm:
        print("Dry run only. Add --confirm to actually send via SMTP.")


def main(argv=None):
    p = argparse.ArgumentParser(prog="outreach", description=__doc__)
    p.add_argument("--leads", default=DEFAULT_LEADS)
    p.add_argument("--suppress", default=DEFAULT_SUPPRESS)
    p.add_argument("--config", default=ROOT / "config" / "company.toml")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("import", help="Merge a CSV (e.g. LinkedIn/CRM export) into leads")
    s.add_argument("csv")
    s.set_defaults(fn=cmd_import)

    for name, fn, h in [("preview", cmd_preview, "Show the first rendered email"),
                        ("render", cmd_render, "Write .eml files to the outbox for review")]:
        s = sub.add_parser(name, help=h)
        s.add_argument("--template", default="introduction")
        s.add_argument("--segment", default="")
        s.add_argument("--outbox", default="outbox")
        s.set_defaults(fn=fn)

    s = sub.add_parser("send", help="Send reviewed outbox emails via SMTP (dry run by default)")
    s.add_argument("--outbox", default="outbox")
    s.add_argument("--limit", type=int, default=int(os.environ.get("OUTREACH_DAILY_LIMIT", "30")))
    s.add_argument("--confirm", action="store_true")
    s.set_defaults(fn=cmd_send)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
