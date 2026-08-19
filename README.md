# Zinfai parser packs

Community-contributed statement parsers for [Zinfai](https://github.com/ZinfaiAdmin/Zinfai).

Zinfai reads bank and broker statements. There are thousands of statement
layouts and no way for one person to write a parser for each of them — so a
parser here is **data, not code**: a JSON document describing where the table
starts, which column means what, and how that bank writes its dates and
numbers. Anyone can contribute one, and nobody has to trust anyone to do it.

## Why this is safe to install

A contribution is not a claim, it is a claim plus the evidence, and the
evidence runs:

1. Every spec ships with a **redacted sample** of the statement it was written
   from and the exact rows it must produce from that sample.
2. CI runs every spec against its own sample on every pull request. If the rows
   don't match, the pack doesn't merge.
3. Your copy of Zinfai does the same check again after downloading, before
   installing anything.

A spec is never executed as code. The only executable fragment a spec may
contain is a regular expression, which is length-capped and compiled by the
schema validator.

Community specs also resolve **last** — behind the parsers that ship with
Zinfai and behind any spec you confirmed yourself. A pack can fill a gap; it
can never replace a parser you already have.

**Fetching packs is off by default.** Turn it on in Settings → Automations
only if you want it.

## What's in a sample

Nothing from your statement. The redactor rebuilds every value from its own
format rather than scrubbing text:

| In your statement | In the sample |
|---|---|
| `RAJESH KUMAR SHARMA` | `JUNIPER KESTREL WILLOW` |
| `50100234567891` | `72833456789013` |
| `1,45,678.90` | `4,21,933.17` |
| `04/01/2026` | `07/01/2026` |
| `UPI-SWIGGY-rajesh@okaxis` | `UPI-NIMBUS-junipe@fabl` |

Names, account numbers, amounts and dates are replaced; the **shape** —
grouping, decimals, masks, date format, the `UPI`/`NEFT`/`POS` markers a parser
keys off — is kept, because that is the part being tested. Balances are
redacted too, so a sample does not add up down the column. That is deliberate:
no parser derives a transaction from the arithmetic between rows.

Zinfai shows you the redacted sample before you contribute it. Read it. If
anything in it still looks like your data, don't submit it — open an issue
instead, because that is a bug in the redactor.

## Contributing a parser

1. In Zinfai, upload a statement from the institution and let it learn the
   layout (Settings → Statement Parsers).
2. Once the parser reads your statements correctly, use **Contribute** on that
   parser. Zinfai builds the redacted sample and hands you a JSON entry.
3. Read the entry.
4. Open a pull request adding it to `packs/community.json` under `specs`.

CI will validate it. If it fails, the error names the exact row and field that
disagreed.

### Running the check yourself

The validator imports Zinfai's own schema and interpreter rather than
reimplementing them — a second implementation would eventually disagree with
the first, and the disagreement would be silent. So it needs a Zinfai checkout:

```bash
ZINFAI_BACKEND=/path/to/zinfai/backend python tools/validate.py packs/community.json
```

**Note:** the Zinfai repository is currently private. CI therefore checks it
out with a `ZINFAI_REPO_TOKEN` secret, which GitHub does not expose to pull
requests from forks. If your PR's validation job fails at the checkout step,
that is why — say so in the PR and a maintainer will run it. Everything after
that step is ordinary and reproducible.

## Ground rules

- **Never submit a sample you have not read.** The redactor is good and it is
  also just software.
- **One institution per entry.** A spec for HDFC savings does not belong in the
  same entry as HDFC credit cards.
- **No personal data in metadata either** — `contributor` is optional and a
  handle is plenty. Don't put your email or account number in it.
- Contributions are licensed under the same terms as this repository (MIT).

## Layout

```
packs/community.json     the pack Zinfai downloads
tools/validate.py        the same validation CI runs
.github/workflows/ci.yml runs every fixture on every PR
```
