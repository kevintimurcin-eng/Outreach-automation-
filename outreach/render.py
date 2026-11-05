"""Render personalised emails from Jinja2 templates."""
from __future__ import annotations

import tomllib
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

from .leads import FIELDS
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path = ROOT / "config" / "company.toml") -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def render(template: str, lead: dict, config: dict, templates_dir: Path = ROOT / "templates") -> tuple[str, str]:
    env = Environment(loader=FileSystemLoader(templates_dir), undefined=StrictUndefined,
                      trim_blocks=False, keep_trailing_newline=True)
    lead = {f: "" for f in FIELDS} | {k: v or "" for k, v in lead.items()}
    text = env.get_template(f"{template}.j2").render(lead=lead, **config).lstrip()
    first, _, body = text.partition("\n")
    if not first.startswith("Subject:"):
        raise ValueError(f"Template {template!r} must start with a 'Subject:' line")
    return first.removeprefix("Subject:").strip(), body.lstrip("\n")


def build_message(lead: dict, subject: str, body: str, config: dict) -> EmailMessage:
    sender = config["sender"]
    msg = EmailMessage()
    msg["From"] = formataddr((f'{sender["name"]} | {config["company"]["name"]}', sender["email"]))
    msg["To"] = formataddr((f'{lead.get("first_name","")} {lead.get("last_name","")}'.strip(), lead["email"]))
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=sender["email"].split("@")[-1])
    msg["List-Unsubscribe"] = f'<mailto:{sender["email"]}?subject=unsubscribe>'
    msg.set_content(body)
    return msg
