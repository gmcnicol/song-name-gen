# Non Sequitur — Random Song Title Generator

**Incoherence is a feature.** Four grammatical patterns, tens of thousands of dictionary words, and no attempt to make the combinations mean anything. All selections are independent: no semantic matching, safety filter, theme, AI scoring or deduplication.

## Browser (GitHub Pages)

Open **`index.html`** in any modern browser, or enable **GitHub Pages** for the `main` branch at **`/(root)`** once the repository is public. Everything works offline; the entire wordlist is embedded in the HTML, with no external requests or dependencies.

Pick a pattern, generate a batch, copy all titles, or press **R** for another batch.

## CLI

Python 3.8+ (standard library only):

```sh
python3 song_titles.py                   # 12 random titles
python3 song_titles.py -n 30            # 30 titles
python3 song_titles.py -p ongoing -n 20 # the fourth pattern
python3 song_titles.py --seed 1979      # reproducible list
python3 -m unittest discover -v         # run tests
```

## Patterns

1. **Verb the Noun** — `Dissect the Banjo`
2. **Noun + coupling phrase + adjective + noun** — `Semaphore Beneath the Liquid Pension`
3. **Noun and the Noun** — `Cemetery and the Apricot`
4. **Verbing [while / as / waiting] the Noun Verbs** — `Dissolving While the Tribunal Sneezes`; waiting takes the form `Dissolving Waiting for the Tribunal to Sneeze`

Only the grammar is constrained. Accidental sense, oddities, repetitions and nonsense are all welcome.

## Editing the website

Edit `web/index.template.html` for layout and JavaScript, or the plain-text files in `wordlists/` to change the vocabulary. Then regenerate the committed GitHub Pages entrypoint:

```sh
python3 scripts/build_page.py
```

The generated `index.html` is self-contained and intentionally committed so Pages can serve it without a build pipeline. The CLI reads the same wordlists directly. The browser randomly selects words using `crypto.getRandomValues` where supported; the Python CLI additionally supports `--seed`.

See [DATA_CREDITS.md](DATA_CREDITS.md) for vocabulary provenance and licensing attribution.

## Daily Bluesky bot (optional)

`bot/post_daily.py` reuses the CLI title generator. It posts at most one title per
**Europe/London calendar day**, using a deterministic AT Protocol TID record key;
re-running it on the same day won't create a second post. There are no unsolicited
mentions by default: optionally supply a list of **bands that have explicitly opted in**.
The bot's public posts aren't semantically edited, and no AI is involved.

Try it without an account or publishing anything:

```sh
python3 -m bot.post_daily --dry-run
```

To enable posting, create a dedicated Bluesky account and an **app password**.
Set `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` as environment variables, then:

```sh
uv run --extra bot python -m bot.post_daily --dry-run  # preview
uv run --extra bot python -m bot.post_daily            # publish once
```

Add opted-in bands to `bot/bands.json` as objects containing `handle` and
`opted_in: true`. Entries without `opted_in: true` are deliberately ignored.
For example: `{"bands": [{"handle": "example.bsky.social", "opted_in": true}]}`.
Only opt in bands with their permission; automatically tagging strangers can be spam.

### Scheduled on Linux/N​​UC via systemd

The repo includes `deploy/non-sequitur.service` and `.timer`. Assuming the repo is
cloned to `~/src/song-name-gen` and `uv` is in `~/.local/bin`, configure a rootless
user timer:

```sh
mkdir -p ~/.config/non-sequitur ~/.config/systemd/user
printf 'BLUESKY_HANDLE=yourbot.bsky.social\nBLUESKY_APP_PASSWORD=your-app-password\n' > ~/.config/non-sequitur/bluesky.env
chmod 600 ~/.config/non-sequitur/bluesky.env
cp deploy/non-sequitur.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now non-sequitur.timer
systemctl --user list-timers non-sequitur.timer
```

The timer runs at 11:17 Europe/London daily, with catch-up after downtime.
Change the `WorkingDirectory` / `ExecStart` paths in the service if your
checkout or `uv` location differs. Check output using
`journalctl --user -u non-sequitur.service -n 50`.
The bot is **not** activated by committing the repo: you'll need to create
credentials and enable the timer yourself. Use `--dry-run` first.

`python3 -m unittest discover -v` tests both the generator and the bot offline.
