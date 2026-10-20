"""Run with: python3 -m unittest discover -v"""
import json
import random
import re
import unittest
from pathlib import Path

from song_titles import PATTERNS, gerund, third_person, title

ROOT = Path(__file__).resolve().parent


class WordForms(unittest.TestCase):
    def test_participles(self):
        for source, expected in {
            "be": "being", "die": "dying", "run": "running", "stop": "stopping",
            "make": "making", "agree": "agreeing", "panic": "panicking",
            "wait": "waiting", "fly": "flying", "talk": "talking",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(gerund(source), expected)

    def test_third_person(self):
        for source, expected in {
            "be": "is", "have": "has", "do": "does", "go": "goes",
            "fly": "flies", "watch": "watches", "buzz": "buzzes", "sing": "sings",
        }.items():
            with self.subTest(source=source):
                self.assertEqual(third_person(source), expected)

    def test_every_pattern_generates(self):
        for pattern in (*PATTERNS, "all"):
            with self.subTest(pattern=pattern):
                titles = [title(random.Random(seed), pattern) for seed in range(12)]
                self.assertEqual(len(titles), 12)
                self.assertTrue(all(t.strip() for t in titles))
                self.assertTrue(all(" the " in t.lower() for t in titles))

    def test_seed_reproducibility(self):
        self.assertEqual(title(random.Random(42), "ongoing"), title(random.Random(42), "ongoing"))

    def test_waiting_while_as_all_reachable(self):
        # We need every connector; random selection is deliberately unbiased.
        results = [title(random.Random(seed), "ongoing") for seed in range(200)]
        self.assertTrue(any(" Waiting for the " in t for t in results))
        self.assertTrue(any(" While the " in t for t in results))
        self.assertTrue(any(" As the " in t for t in results))

    def test_html_embeds_wordlists_and_all_patterns(self):
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<script type="application/json" id="lexicon">(.*?)</script>', page, re.DOTALL)
        self.assertIsNotNone(match)
        embedded = json.loads(match.group(1))
        for category in ("nouns", "verbs", "adjectives"):
            expected = (ROOT / "wordlists" / f"{category}.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(embedded[category], expected)
        self.assertIn('option value="ongoing"', page)
        self.assertIn("'verb', 'coupled', 'and', 'ongoing'", page)


if __name__ == "__main__":
    unittest.main()
