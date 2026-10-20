#!/usr/bin/env python3
"""Build the self-contained GitHub Pages homepage from the source wordlists.

Run from any working directory: python3 scripts/build_page.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web" / "index.template.html"
OUTPUT = ROOT / "index.html"
MARKER = "__LEXICON_JSON__"


def build() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        raise ValueError("Expected exactly one lexicon placeholder in the HTML template")
    lexicon = {}
    for category in ("adjectives", "nouns", "verbs"):
        text = (ROOT / "wordlists" / f"{category}.txt").read_text(encoding="utf-8")
        lexicon[category] = [word for line in text.splitlines() if (word := line.strip())]
        if not lexicon[category]:
            raise ValueError(f"Empty wordlist: {category}")
    data = json.dumps(lexicon, ensure_ascii=False, separators=(",", ":"))
    # The embedded JSON sits in a <script> tag, so escape literal tag delimiters.
    data = data.replace("<", "\\u003c")
    OUTPUT.write_text(template.replace(MARKER, data), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with " + ", ".join(
        f"{len(lexicon[k]):,} {k}" for k in ("nouns", "verbs", "adjectives")))


if __name__ == "__main__":
    build()
