"""Offer one nonsensical song title on Bluesky per UK calendar day.

The bot only mentions bands explicitly opted in via bot/bands.json.
AT Protocol TID record keys are derived from the date, making retries idempotent.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timezone
import json
import os
from pathlib import Path
import random
import re
from zoneinfo import ZoneInfo

from song_titles import title

BANDS_PATH = Path(__file__).with_name("bands.json")
BRITISH_TIME = ZoneInfo("Europe/London")
TID_ALPHABET = "234567abcdefghijklmnopqrstuvwxyz"
HANDLE_RE = re.compile(r"^(?=.{4,253}$)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+$", re.I)


def opted_in_bands(path: Path = BANDS_PATH) -> list[str]:
    """Only explicit, current opt-ins may receive automatic @mentions."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("bands"), list):
        raise ValueError("bands.json must contain an array called 'bands'")
    bands = []
    for entry in data["bands"]:
        if not isinstance(entry, dict):
            raise ValueError("Each band must be a JSON object")
        handle = entry.get("handle", "")
        if entry.get("opted_in") is True:
            if not isinstance(handle, str) or not HANDLE_RE.fullmatch(handle):
                raise ValueError(f"Invalid opted-in handle: {handle!r}")
            if handle.lower() not in bands:
                bands.append(handle.lower())
    return bands


def daily_tid(day: date) -> str:
    """Deterministic, valid 13-character TID based on 12:00 UTC for this date.

    The lexicon for app.bsky.feed.post requires a TID rkey. A fixed TID per
    date means a retry won't emit a second post, even after process crashes.
    """
    micros = int(datetime.combine(day, time(12), tzinfo=timezone.utc).timestamp() * 1_000_000)
    value = micros << 10
    result = ""
    for _ in range(13):
        result = TID_ALPHABET[value & 31] + result
        value >>= 5
    return result


def offer(rng: random.Random, handles: list[str]) -> tuple[str, str | None]:
    """Format the gift; retain true random word collisions from the generator."""
    for _ in range(100):
        generated = title(rng)
        handle = rng.choice(handles) if handles else None
        greeting = f"@{handle} — you can have that." if handle else "You can have that."
        message = f"“{generated}”\n\n{greeting}"
        if len(message) <= 300 and len(message.encode("utf-8")) <= 3000:
            return message, handle
    raise RuntimeError("Could not generate a title within Bluesky's post length limit")


def publish(day: date, text: str, handle: str | None) -> str:
    """Use a standard Bluesky app password, never the account password."""
    from atproto import Client, client_utils, models
    from atproto.exceptions import BadRequestError

    identifier = os.environ["BLUESKY_HANDLE"]
    app_password = os.environ["BLUESKY_APP_PASSWORD"]
    client = Client()
    client.login(identifier, app_password)

    # Build an actual mention facet, not an inert text handle. The handle is
    # resolved at posting time, so account renames can't silently target others.
    facets = None
    if handle:
        did = client.resolve_handle(handle).did
        prefix, suffix = text.split(f"@{handle}", 1)
        builder = client_utils.TextBuilder().text(prefix).mention(f"@{handle}", did).text(suffix)
        facets = builder.build_facets()
        text = builder.build_text()

    record = models.AppBskyFeedPost.Record(
        text=text,
        created_at=client.get_current_time_iso(),
        facets=facets,
        langs=["en"],
    )
    try:
        result = client.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=client.me.did,
                collection=models.ids.AppBskyFeedPost,
                rkey=daily_tid(day),
                record=record,
            )
        )
        return str(result.uri)
    except BadRequestError as exc:
        # A previous attempt might already have posted successfully before
        # losing its response; don't treat duplicate creation as a new failure.
        if "alreadyexists" not in str(exc).lower() and "already exists" not in str(exc).lower():
            raise
        return f"already posted ({day.isoformat()})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a daily unrequested song-title gift to Bluesky")
    parser.add_argument("--dry-run", action="store_true", help="Preview text; no credentials or network needed")
    parser.add_argument("--date", type=date.fromisoformat, help="Override today's UK date (for local testing)")
    parser.add_argument("--bands", type=Path, default=BANDS_PATH, help="JSON file of opted-in Bluesky band handles")
    args = parser.parse_args()
    today = args.date or datetime.now(BRITISH_TIME).date()
    text, handle = offer(random.SystemRandom(), opted_in_bands(args.bands))
    print(text)
    if args.dry_run:
        print(f"\n(dry run; date={today.isoformat()}, record key={daily_tid(today)})")
        return
    uri = publish(today, text, handle)
    print(f"\n{uri}")


if __name__ == "__main__":
    main()
