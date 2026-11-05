# Outreach automation – Nordic Group introductions

Personalised introduction emails from Nordic Group (Marbella) to developers, investors,
agencies and hotels – created as **Gmail drafts** so every email is reviewed before it goes out.
No third-party lead platforms are used.

## How it works (with Claude + the Gmail connector)
1. Ask Claude to research companies in a category, e.g. *"property developers on the Costa del Sol"*.
   Claude uses web search and only uses **general contact emails published by the company itself**
   (info@, contact@) – it never guesses personal addresses.
2. Claude writes a personal opening line and three tailored value points per company,
   renders `templates/introduction.html.j2`, and puts each email in your **Gmail drafts**.
3. You review, edit and press send in Gmail. Log replies/opt-outs in `data/suppression.csv`.

## Templates
| File | Use |
|---|---|
| `templates/introduction.html.j2` | Designed HTML introduction (black header, sand accents, CTA button) |
| `templates/introduction.j2` | Plain-text introduction, adapts by `segment` |
| `templates/followup.j2` | Short follow-up one week later |

Per-lead fields for the HTML template: `subject`, `headline`, `greeting`, `personal_line`,
`offer_intro`, `points` (list of 3 title/text pairs), `ask`. All have sensible defaults
except `personal_line`. Firm details live in `config/company.toml`.

The HTML email uses no remote images or web fonts – this keeps it out of spam/promotions
folders and renders the same in Gmail, Outlook and Apple Mail.

## Local CLI (optional)
```bash
pip install -r requirements.txt
python -m outreach import my_contacts.csv
python -m outreach preview --template introduction
python -m outreach render  --template introduction     # writes .eml files to outbox/
python -m pytest
```

## Rules for cold email (please read)
- **Spain (LSSI art. 21)** generally requires prior consent for commercial email, also B2B.
  We therefore write only to generic company inboxes, keep it a genuine one-to-one business
  introduction, and always include the postal address and an opt-out line.
- Keep volumes low (a handful per day), and never email anyone in `data/suppression.csv` again.
