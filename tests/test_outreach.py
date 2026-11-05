from pathlib import Path

from outreach import leads as L
from outreach.render import build_message, load_config, render
from outreach.send import send_outbox, write_outbox
from outreach.sources.google_places import domain_of

ROOT = Path(__file__).resolve().parent.parent


def test_render_introduction_personalises_by_segment():
    cfg = load_config()
    lead = {"email": "a@x.com", "first_name": "Anna", "last_name": "B", "company": "Acme AB",
            "segment": "developer"}
    subject, body = render("introduction", lead, cfg)
    assert "Acme AB" in subject
    assert body.startswith("Hi Anna,")
    assert "feasibility" in body
    assert cfg["compliance"]["postal_address"] in body


def test_render_handles_missing_fields():
    subject, body = render("followup", {"email": "a@x.com"}, load_config())
    assert "your next project" in subject and "Hi there," in body


def test_merge_dedupes_and_fills_blanks():
    a = [{"email": "A@x.com", "company": ""}]
    b = [{"email": "a@x.com", "company": "X"}, {"email": "", "domain": "y.com", "company": "Y"}]
    merged = L.merge([{k: v for k, v in r.items()} | {f: r.get(f, "") for f in L.FIELDS} for r in a], b)
    assert len(merged) == 2 and merged[0]["company"] == "X"


def test_sendable_respects_suppression_and_validity():
    rows = [{"email": "ok@x.com"}, {"email": "bad"}, {"email": "STOP@x.com"}, {"email": "ok@x.com"}]
    assert [r["email"] for r in L.sendable(rows, {"stop@x.com"})] == ["ok@x.com"]


def test_outbox_roundtrip_and_dry_run(tmp_path):
    cfg = load_config()
    lead = {"email": "a@x.com", "first_name": "A", "last_name": "", "company": "X"}
    msg = build_message(lead, *render("introduction", lead, cfg), cfg)
    assert "unsubscribe" in msg["List-Unsubscribe"]
    paths = write_outbox([msg], tmp_path)
    assert paths[0].exists()
    assert send_outbox(tmp_path, limit=5)[0].startswith("[dry-run]")


def test_domain_of():
    assert domain_of("https://www.Example.se/kontakt") == "example.se"
