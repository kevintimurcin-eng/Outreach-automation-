# Outreach automation – architecture firm introductions

Find prospective clients (property developers, hotels, public bodies…), look up
decision-maker emails, and send a personalised introduction email about your studio.

```
find companies ──► find emails ──► review leads.csv ──► render to outbox/ ──► review ──► send
(Google Places)     (Hunter.io)     (Excel/Sheets)       (.eml files)                    (SMTP or Gmail drafts)
```

## Setup
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add your API keys (local use only)
```
Edit **`config/company.toml`** with your firm's name, specialties, portfolio link,
sender details and postal address. Edit the wording in **`templates/`**.

## Usage
```bash
# 1. Find target companies (any wording works, e.g. "real estate investors Costa del Sol")
python -m outreach find-companies "property developers in Marbella" --segment developer

# 2. Find decision-maker emails for those companies' websites
python -m outreach find-emails --max-domains 10

# 2b. Or import contacts from another platform (LinkedIn Sales Navigator, CRM, trade-fair list…)
python -m outreach import my_export.csv

# 3. Preview, then write every email to outbox/ for review
python -m outreach preview --template introduction
python -m outreach render  --template introduction --segment developer

# 4. Send (dry run unless --confirm). Spreads sends 20–60 s apart, max OUTREACH_DAILY_LIMIT.
python -m outreach send --confirm
```
Use `--template followup` a week later for those who didn't reply.

Leads live in `data/leads.csv` (columns: email, first_name, last_name, position,
company, domain, city, segment, source, notes). Anyone who replies "unsubscribe"
goes in `data/suppression.csv` and is never emailed again.

### Templates
`templates/*.j2` are Jinja2. The first line is `Subject: …`. Available fields:
`lead.*` (any CSV column), `company.*`, `sender.*`, `compliance.*` from `company.toml`.
The introduction adapts its pitch by `lead.segment` (`developer`, `investor`, `hospitality`, `public`, other).

### Using it with Claude
In a Claude session with the Gmail connector, ask Claude to *"render the outbox and
create Gmail drafts"* – you then review and send from Gmail yourself.

## Rules for cold email (please read)
- **Spain (LSSI art. 21) and Denmark require prior consent** for commercial email, even
  to businesses. Since you are based in Spain, the safest route is to email generic company addresses
  (info@, contact@) or people who have given consent. In Sweden and most other EU countries, B2B email to a work address is
  usually allowed under GDPR legitimate interest if it is relevant to the person's role.
  Check the rules for the recipient's country; when in doubt, use generic company
  addresses (info@, contact@) or get legal advice.
- Always identify your firm, include a postal address and an easy opt-out (built in).
- Only store business contact data, record its `source`, and delete leads you don't use.
- Keep volumes low (≤30/day per mailbox) to protect your domain's reputation.
