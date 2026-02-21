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
