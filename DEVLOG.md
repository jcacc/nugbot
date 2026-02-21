# nugbot devlog

## 2026-02-20 — Migrate to discord.py 2.x

Upgraded from discord.py 1.7.1 (unmaintained) to 2.x.

**Changes:**
- Added `discord.Intents` with `message_content = True` (privileged intent, enabled in Dev Portal)
- Made `load_nugs()` async; `bot.load_extension()` now awaited
- All cog `setup()` functions made async; `bot.add_cog()` now awaited
- Simplified `requirements.txt` to direct deps only, dropped pinned transitive packages

**Deployed** to lampPost via scp, service restarted on reboot. All nugs loaded clean.
