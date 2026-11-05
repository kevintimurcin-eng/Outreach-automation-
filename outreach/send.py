"""Write emails to an outbox folder for review, and optionally send them via SMTP."""
from __future__ import annotations

import os
import random
import smtplib
import time
from email import policy
from email.parser import BytesParser
from pathlib import Path


def write_outbox(messages, outbox: Path) -> list[Path]:
    outbox.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, msg in enumerate(messages, 1):
        to = msg["To"].addresses[0].addr_spec.replace("@", "_at_")
        p = outbox / f"{i:03d}_{to}.eml"
        p.write_bytes(bytes(msg))
        paths.append(p)
    return paths


def send_outbox(outbox: Path, limit: int, dry_run: bool = True, sent_dir: Path | None = None,
                delay=(20, 60)) -> list[str]:
    files = sorted(outbox.glob("*.eml"))[:limit]
    sent_dir = sent_dir or outbox / "sent"
    done = []
    if dry_run:
        return [f"[dry-run] would send {f.name}" for f in files]
    host, port = os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        for n, f in enumerate(files):
            msg = BytesParser(policy=policy.default).parse(f.open("rb"))
            smtp.send_message(msg)
            sent_dir.mkdir(parents=True, exist_ok=True)
            f.rename(sent_dir / f.name)
            done.append(f"sent {f.name}")
            if n < len(files) - 1:
                time.sleep(random.uniform(*delay))  # spread out sends; protects your domain reputation
    return done
