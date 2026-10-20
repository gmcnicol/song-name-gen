"""No network, SDK dependency or app password needed for these tests."""
from datetime import date
import json
from pathlib import Path
import random
import tempfile
import unittest

from bot.post_daily import daily_tid, offer, opted_in_bands


class BotTests(unittest.TestCase):
    def test_same_day_has_same_tid(self):
        self.assertEqual(daily_tid(date(2026, 10, 20)), daily_tid(date(2026, 10, 20)))
        self.assertNotEqual(daily_tid(date(2026, 10, 20)), daily_tid(date(2026, 10, 21)))

    def test_tid_is_correct_shape(self):
        value = daily_tid(date(2026, 10, 20))
        self.assertEqual(len(value), 13)
        self.assertTrue(all(x in "234567abcdefghijklmnopqrstuvwxyz" for x in value))

    def test_only_explicit_opt_ins(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "bands.json"
            file.write_text(json.dumps({"bands": [
                {"handle": "yes.bsky.social", "opted_in": True},
                {"handle": "no.bsky.social", "opted_in": False},
                {"handle": "missing.bsky.social"},
                {"handle": "YES.bsky.social", "opted_in": True},
            ]}))
            self.assertEqual(opted_in_bands(file), ["yes.bsky.social"])

    def test_empty_roster_generates_normal_public_post(self):
        post, handle = offer(random.Random(10), [])
        self.assertIsNone(handle)
        self.assertTrue(post.endswith("You can have that."))
        self.assertLessEqual(len(post), 300)

    def test_opted_in_handle_is_mentioned(self):
        post, handle = offer(random.Random(14), ["someband.bsky.social"])
        self.assertEqual(handle, "someband.bsky.social")
        self.assertIn("@someband.bsky.social — you can have that.", post)


if __name__ == "__main__":
    unittest.main()
