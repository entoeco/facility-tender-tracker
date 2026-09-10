# Sussex Technical Facilities — Opportunity Tracker

Scrapes UK public procurement notices (Contracts Finder + Find a Tender) for open
tenders that could use one of Sussex's technical facilities (MRI, NMR, mass spec,
cryo-EM, mechanical workshop, sequencing, etc.), scores them by keyword match, and
shows them in a Streamlit dashboard for manual review.

No AI/LLM involved and nothing is submitted automatically — this only surfaces a
shortlist for a human to review and act on.

## Local setup

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Click **Refresh now** in the sidebar to run the first scrape (populates
`data/opportunities.db`, a local SQLite file that is not committed to git).

## How it works

- `scraper/sources.py` — pulls raw OCDS release data from the Contracts Finder and
  Find a Tender APIs (no keyword search exists server-side, so this pulls a recent
  date window and everything is filtered locally).
- `scraper/normalize.py` — converts each source's OCDS shape into one common record.
- `scraper/filter.py` — scores each record against `config.py`'s facility/sector
  keyword lists.
- `scraper/db.py` — upserts matched records into SQLite; keeps a separate `status`
  table (new/seen/dismissed/applied) that a refresh never overwrites.
- `scraper/pipeline.py` — chains the above into one run, callable from the app or CLI
  (`py -m scraper.pipeline`).
- `app.py` — the Streamlit dashboard: refresh button, filters, per-row status control.

## Tuning matches

Edit `config.py`'s `FACILITY_KEYWORDS` and `SECTOR_KEYWORDS` dicts to add/remove
keywords or facilities. No code changes needed elsewhere.

## Known scope limits (v1)

- Only Contracts Finder and Find a Tender are scraped — both cover UK public-sector
  procurement broadly (including university/NHS/research-body buyers), but do not
  include research council *grant* calls (e.g. UKRI funding opportunities) or
  charity-funded calls (e.g. Wellcome), which aren't procurement notices and don't
  have the same kind of public API. Those would need a separate, more fragile
  HTML-scraping addition if wanted later.
- Matching is plain keyword scoring against title + description text — no LLM
  relevance pass, no drafting.
