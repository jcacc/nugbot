# nugbot devlog

## 2026-02-20 — Migrate to discord.py 2.x

Upgraded from discord.py 1.7.1 (unmaintained) to 2.x.

**Changes:**
- Added `discord.Intents` with `message_content = True` (privileged intent, enabled in Dev Portal)
- Made `load_nugs()` async; `bot.load_extension()` now awaited
- All cog `setup()` functions made async; `bot.add_cog()` now awaited
- Simplified `requirements.txt` to direct deps only, dropped pinned transitive packages

**Deployed** to lampPost via scp, service restarted on reboot. All nugs loaded clean.

**Repo:** Deleted standalone `jcacc/nugbot`, re-established as a proper fork of `mulcare/nugbot`. Opened PR #1 with the 2.x migration.

## 2026-02-21 — Add drewhal MegaHAL cog

Added `nugs/drewhal.py` — a MegaHAL Markov chain cog that trains on `drewzer0.txt` and randomly babbles to a Discord channel every 30 minutes to 3 hours, unprompted.

**Notes:**
- `megahal` installed via pip on lampPost
- Brain persists to `nugs/drewhal.brain` — only trains once on first run
- Training took ~12 minutes for 25k lines on the Pi
- Fixed megahal's `boundary()` `IndexError` (crashes on lines ending with apostrophe) by wrapping each `learn()` call in a try/except and skipping bad lines (4 skipped total)
- Fixed encoding by reading drewzer0.txt with `utf-8/errors='replace'` instead of relying on megahal's file open
- Added `-u` flag to systemd service (`python3 -u`) to enable unbuffered stdout in journald

## 2026-02-21 — Add drewstats cog

Added `nugs/drewstats.py` — reads drewzer0.txt and posts a Discord embed with stats: total lines, total words, average line length, top 10 words (stopwords filtered), and the longest line. Command: `.drewstats`.

## 2026-02-21 — Expand fm cog; add sysinfo + youtube; slash commands

### fm cog — full fmbot-style rewrite (both bots)
Rewrote `nugs/fm.py` (and sharebro's `cogs/fm.py`) with SQLite storage and a full command set:

**Storage:** Migrated from flat `fm_users.json` to SQLite (`fm.db`). Auto-migrates on first load.

**New commands:** `plays`, `toptracks`, `topalbums`, `topartists`, `track`, `trackplays`, `artist`, `artistplays`, `album`, `albumplays`, `whoknowstrack` (wktr/wt), `whoknowsalbum` (wkab/wa), `taste`, `overview`, `streak`, `serverartists`, `serveralbums`, `servertracks`

**Bug fixes:**
- `whoknows` family: `guild.get_member()` returns None without Members intent — added `_guild_registered()` helper that falls back to `guild.fetch_member()` for cache misses
- `taste`: increased artist fetch limit from 50 → 1000 for accurate overlap

**lampPost note:** `~/nugbot/` is not a git repo — deploy via scp.

### sysinfo cog
Added `nugs/sysinfo.py` — `.sysinfo` / `.top` shows a system snapshot embed: CPU %, memory, disk, uptime, top 5 processes by CPU. Uses `psutil`.

### youtube cog
Added `nugs/youtube.py` — `.youtube` / `.yt <query>` searches YouTube via `yt-dlp` and returns top 5 results as an embed with title, channel, duration, and thumbnail.

**Bug:** `default_search: 'ytsearch5'` + `extract_flat: True` returns a broken structure. Fixed by passing `ytsearch5:{query}` directly.

### Slash commands
Converted all cog commands to `@commands.hybrid_command()` — work as both prefix (`.`) and slash (`/`). Period parameters use `Literal` type for dropdown UI. `tree.sync()` called in `setup_hook`.

## 2026-02-21 — Add fm cog (Last.fm); moved to sharebro

Added `nugs/fm.py` with Last.fm integration: `.setfm <username>`, `.fm [member]` (now playing / last played), `.recent [member]` (last 5 tracks), `.topartists [member] [period]`. User registrations stored in `fm_users.json`.

Decided to deploy fm on sharebro instead of nugbot — better fit for that server. Removed fm from nugbot's nug list; deployed to `/home/jca/dev/python/sharebro/cogs/fm.py` on lampPost.
