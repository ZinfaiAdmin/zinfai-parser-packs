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

Start here whichever way you submit:

1. Get the parser working in Zinfai first (Settings → Statement Parsers). A
   parser that has not read your own statements correctly is not ready.
2. Click **Contribute** on it. Zinfai builds the redacted fixture.
3. **Read the fixture.** Every value in it should be obviously fake. If you
   recognise anything — a payee, a partial account number, an amount you
   remember — stop and open an issue. That is a redactor bug and we want it.

Then pick one of the two routes below. They end in the same place; the first is
less work for you and more for us, which is the right way round.

### Let Zinfai fill in the form

4. Click **Submit it**. Zinfai opens the contribution issue form with the
   institution and the entry already filled in.
5. Read it — this is your last look at the fixture before it is public — tick
   the two boxes and press **Submit new issue**. Nothing has been sent until
   you do.
6. The issue is labelled with the institution automatically (`bank: hdfc-bank`,
   and so on), and a maintainer runs the validator and opens the pull request
   for you.

Zinfai ships no credential and cannot post anything on your behalf. The button
fills in a form; you are the one who submits it. If you close the tab without
submitting, nothing has happened and you can start again.

### Open the pull request yourself

Use this if you would rather do it by hand, or if Zinfai tells you the entry is
too large to fit into a pre-filled issue.

4. Copy or download the entry from the same dialog.
5. Append it to the `specs` array in `packs/community.json`.
6. Run `python tools/validate.py packs/community.json`.
7. Open a pull request.

### Labels

Contributions are labelled `parser-contribution` plus one `bank: …` label taken
from the Institution field, so you can check whether someone has already
submitted your bank before writing a parser for it:

```
https://github.com/ZinfaiAdmin/zinfai-parser-packs/issues?q=label:"bank: hdfc-bank"
```

Keep the Institution field to the plain name — "HDFC Bank", not "HDFC Bank
savings statement PDF" — or it becomes its own label and groups with nothing.

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
