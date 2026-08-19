# Contributing a parser

## What you're contributing

One JSON entry with three parts:

- `spec` — the layout description: where the table starts, which column is
  which, how dates and numbers are written.
- `fixture` — a redacted copy of a statement in that layout. Zinfai generates
  this; do not write one by hand and do not edit one.
- `expected` — the exact rows the spec must produce from that fixture. Zinfai
  generates this too.

CI runs `spec` against `fixture` and compares against `expected`. That is the
whole review: if they agree, the parser demonstrably works; if they don't, it
demonstrably doesn't.

## Steps

1. Get the parser working in Zinfai first (Settings → Statement Parsers). A
   parser that has not read your own statements correctly is not ready.
2. Click **Contribute** on it. Zinfai builds the redacted fixture.
3. **Read the fixture.** Every value in it should be obviously fake. If you
   recognise anything — a payee, a partial account number, an amount you
   remember — stop and open an issue. That is a redactor bug and we want it.
4. Append the entry to the `specs` array in `packs/community.json`.
5. Run `python tools/validate.py packs/community.json`.
6. Open a pull request.

## What gets rejected

- A spec that does not reproduce its own fixture.
- A duplicate `spec.id`. Pick a new one, e.g. `hdfc_bank_savings_v2`.
- A fixture with anything real in it.
- An entry with a contributor field containing an email address, account
  number, or anything else you would not post publicly.
- A `bank_key` that collides with an institution Zinfai already parses with
  hand-written code. Those parsers win anyway, so the entry would be dead
  weight — open an issue instead and say what the built-in gets wrong.

## Spec reference

The schema is defined in exactly one place — `backend/app/services/parser_spec.py`
in the Zinfai source — and that is the file both Zinfai and this repo's CI
validate against. Read its docstrings rather than a copy kept here, which would
drift.

Two engines exist:

- `excel_table` — spreadsheets and CSVs. Finds a header row, maps columns to
  fields by header alias or by position.
- `pdf_text_regex` — PDFs. One regular expression per line, with named groups
  (`date`, `description`, `debit`, `credit`, `amount`, `balance`, `indicator`).

Regular expressions are length-capped and compiled by the validator. Nothing in
a spec is ever executed as code.
