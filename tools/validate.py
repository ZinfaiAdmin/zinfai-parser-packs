#!/usr/bin/env python3
"""Validate a parser pack: every spec must reproduce its own redacted sample.

This is the same check Zinfai runs after downloading a pack, deliberately: a
contributor should be able to see the exact failure CI will see, and a reviewer
should not have to take a pull request's word for anything.

It works by importing Zinfai's own parser modules rather than reimplementing
them, because a second implementation would eventually disagree with the first
and the disagreement would be silent. Point ``ZINFAI_BACKEND`` at a Zinfai
checkout's ``backend`` directory, or let CI do it for you.

    python tools/validate.py packs/community.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _load_zinfai():
    """Put Zinfai's backend on the import path and return the pack module."""
    backend = os.environ.get("ZINFAI_BACKEND")
    candidates = [Path(backend)] if backend else []
    candidates += [
        Path(__file__).resolve().parent.parent / "zinfai" / "backend",
        Path(__file__).resolve().parent.parent.parent / "Zinfai" / "backend",
    ]

    for path in candidates:
        if (path / "app" / "services" / "parser_pack.py").exists():
            sys.path.insert(0, str(path))
            # Zinfai's settings object insists on these at import time, and
            # importing the interpreter constructs an engine (though it never
            # connects). Nothing here opens a database or signs anything — a
            # spec is only ever run against an in-memory fixture — so these
            # placeholders are correct rather than merely convenient. The URL
            # has to be Postgres-shaped because the engine is configured with
            # pooling options SQLite rejects.
            os.environ.setdefault(
                "DATABASE_URL", "postgresql://packs:packs@127.0.0.1:5432/packs",
            )
            os.environ.setdefault("SECRET_KEY", "pack-validation-only")
            os.environ.setdefault("ENVIRONMENT", "test")

            from app.services import parser_pack

            return parser_pack

    sys.exit(
        "Could not find a Zinfai backend to validate against.\n"
        "Set ZINFAI_BACKEND=/path/to/Zinfai/backend and try again."
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"No such pack: {path}")
        return 2

    parser_pack = _load_zinfai()

    try:
        document = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"{path}: not valid JSON — {exc}")
        return 1

    try:
        result = parser_pack.validate_pack(document)
    except parser_pack.ParserPackError as exc:
        print(f"{path}: {exc}")
        return 1

    for entry in result.entries:
        if entry.ok:
            print(f"  ok      {entry.spec_id} ({entry.rows_produced} rows)")
        else:
            print(f"  FAILED  {entry.spec_id}: {entry.reason}")

    if result.rejected:
        print(
            f"\n{len(result.rejected)} of {len(result.entries)} spec(s) do not "
            f"reproduce their own sample."
        )
        return 1

    print(f"\nAll {len(result.entries)} spec(s) reproduce their samples exactly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
