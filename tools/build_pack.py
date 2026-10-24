#!/usr/bin/env python3
"""Fold every contribution into the pack Zinfai downloads.

Zinfai installs fetch ``packs/community.json`` and nothing else. A contribution
arrives as its own one-spec pack under ``contributions/``; until it is folded
into ``community.json`` no install ever sees it, so a merged pull request on
its own shares nothing. CI runs this after every merge and once a day.

    python tools/build_pack.py            # rewrite packs/community.json
    python tools/build_pack.py --check    # exit 1 if it would change anything

Each contribution is validated again here: a spec that no longer reproduces its
own sample under the current interpreter is left out, and named. Re-running is
a no-op: a spec already in the pack, under any id, is not added twice. Two
different layouts that happen to share an id keep both, the later one renamed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import _load_zinfai  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "packs" / "community.json"
CONTRIBUTIONS = ROOT / "contributions"


def _body(entry: dict) -> str:
    """The spec without its id, so a renamed copy is still recognised."""
    spec = {k: v for k, v in entry["spec"].items() if k != "id"}
    return json.dumps(spec, sort_keys=True)


def _free_id(wanted: str, taken: set[str]) -> str:
    if wanted not in taken:
        return wanted
    n = 2
    while f"{wanted}_{n}" in taken:
        n += 1
    return f"{wanted}_{n}"


def fold(parser_pack) -> tuple[dict, list[str]]:
    pack = json.loads(PACK.read_text())
    entries = list(pack.get("specs", []))
    ids = {e["spec"]["id"] for e in entries}
    bodies = {_body(e) for e in entries}
    log: list[str] = []

    for path in sorted(CONTRIBUTIONS.glob("*.json")):
        try:
            document = json.loads(path.read_text())
            result = parser_pack.validate_pack(document, name=path.stem)
        except (json.JSONDecodeError, parser_pack.ParserPackError) as exc:
            log.append(f"  skipped {path.name}: {exc}")
            continue
        good = {r.spec_id for r in result.entries if r.ok}
        for r in result.entries:
            if not r.ok:
                log.append(f"  skipped {path.name} → {r.spec_id}: {r.reason}")
        for entry in document.get("specs", []):
            spec_id = entry.get("spec", {}).get("id")
            if spec_id not in good or _body(entry) in bodies:
                continue
            entry = json.loads(json.dumps(entry))
            entry["spec"]["id"] = _free_id(spec_id, ids)
            entries.append(entry)
            ids.add(entry["spec"]["id"])
            bodies.add(_body(entry))
            log.append(f"  added   {entry['spec']['id']} from {path.name}")

    folded = parser_pack.build_pack(entries, name=pack.get("name", "community"))
    if entries == pack.get("specs", []):
        folded["generated_at"] = pack.get("generated_at")  # nothing changed
    result = parser_pack.validate_pack(folded)
    if result.rejected:  # pragma: no cover - every entry was proved above
        raise SystemExit("The folded pack does not validate: "
                         + "; ".join(f"{r.spec_id}: {r.reason}" for r in result.rejected))
    return folded, log


def main(argv: list[str]) -> int:
    folded, log = fold(_load_zinfai())
    print("\n".join(log) or "  nothing new to fold")
    text = json.dumps(folded, indent=2, ensure_ascii=True) + "\n"
    if text == PACK.read_text():
        print("packs/community.json is up to date.")
        return 0
    if "--check" in argv:
        print("packs/community.json is out of date; run tools/build_pack.py.")
        return 1
    PACK.write_text(text)
    print(f"packs/community.json now carries {len(folded['specs'])} spec(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
