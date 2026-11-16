#!/usr/bin/env python3
"""Generate semantically unrelated song titles using grammatical templates.

No meaning-matching, similarity model or semantic filtering is used.
"""

from __future__ import annotations

import argparse
import random
from functools import lru_cache
from pathlib import Path

WORDLISTS = Path(__file__).resolve().parent / "wordlists"
COUPLERS = (
    "above", "after", "against", "alongside", "amid", "among", "around",
    "atop", "before", "behind", "below", "beneath", "beside", "beyond",
    "despite", "during", "inside", "near", "outside", "over", "past",
    "through", "towards", "under", "underneath", "within", "without",
    "with", "in front of", "instead of",
)
PATTERNS = ("verb", "coupled", "and", "ongoing", "the")
TIMING_LINKS = ("while", "as", "waiting")


@lru_cache(maxsize=3)
def words(category: str) -> tuple[str, ...]:
    path = WORDLISTS / f"{category}.txt"
    try:
        result = tuple(w.strip() for w in path.read_text(encoding="utf-8").splitlines() if w.strip())
    except OSError as exc:
        raise SystemExit(f"Cannot read wordlist {path}: {exc}") from exc
    if not result:
        raise SystemExit(f"Wordlist {path} is empty")
    return result


@lru_cache(maxsize=1)
def the_words() -> tuple[str, ...]:
    """Any dictionary word can follow 'The', including the article itself."""
    return (*words("nouns"), *words("adjectives"), *words("verbs"), "the")


def gerund(verb: str) -> str:
    """Form a present participle, without inferring anything about the word's meaning."""
    irregular = {"be": "being", "see": "seeing", "die": "dying", "lie": "lying", "tie": "tying"}
    if verb in irregular:
        return irregular[verb]
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("e") and not verb.endswith(("ee", "ye", "oe")):
        return verb[:-1] + "ing"
    if verb.endswith("c"):
        return verb + "king"
    # Double final consonant in a one-syllable consonant-vowel-consonant verb.
    vowels = "aeiou"
    groups = sum(char in vowels and (i == 0 or verb[i - 1] not in vowels)
                 for i, char in enumerate(verb))
    if (groups == 1 and len(verb) >= 3 and verb[-1] not in vowels + "wxy"
            and verb[-2] in vowels and verb[-3] not in vowels):
        return verb + verb[-1] + "ing"
    return verb + "ing"


def third_person(verb: str) -> str:
    """Form a simple present third-person verb."""
    irregular = {"be": "is", "have": "has", "do": "does", "go": "goes"}
    if verb in irregular:
        return irregular[verb]
    if len(verb) > 1 and verb.endswith("y") and verb[-2] not in "aeiou":
        return verb[:-1] + "ies"
    if verb.endswith(("s", "sh", "ch", "x", "z", "o")):
        return verb + "es"
    return verb + "s"


def title(rng: random.Random, pattern: str = "all") -> str:
    if pattern == "all":
        pattern = rng.choice(PATTERNS)

    noun = lambda: rng.choice(words("nouns")).capitalize()
    if pattern == "verb":
        return f"{rng.choice(words('verbs')).capitalize()} the {noun()}"
    if pattern == "coupled":
        connector = rng.choice(COUPLERS)
        adjective = rng.choice(words("adjectives")).capitalize()
        return f"{noun()} {connector.capitalize()} the {adjective} {noun()}"
    if pattern == "and":
        return f"{noun()} and the {noun()}"
    if pattern == "ongoing":
        first_verb = gerund(rng.choice(words("verbs"))).capitalize()
        link = rng.choice(TIMING_LINKS)
        if link == "waiting":
            return f"{first_verb} Waiting for the {noun()} to {rng.choice(words('verbs')).capitalize()}"
        return f"{first_verb} {link.capitalize()} the {noun()} {third_person(rng.choice(words('verbs'))).capitalize()}"
    if pattern == "the":
        return f"The {rng.choice(the_words()).capitalize()}"
    raise ValueError(f"Unknown pattern: {pattern}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Grammatical song titles; semantic nonsense by design.")
    parser.add_argument("-n", "--count", type=int, default=12, help="Titles to generate (default: 12)")
    parser.add_argument("-p", "--pattern", choices=("all", *PATTERNS), default="all")
    parser.add_argument("--seed", help="Repeat a particular sequence of titles")
    args = parser.parse_args()
    if not 1 <= args.count <= 10000:
        parser.error("--count must be between 1 and 10000")
    rng = random.Random(args.seed)
    for _ in range(args.count):
        print(title(rng, args.pattern))


if __name__ == "__main__":
    main()
