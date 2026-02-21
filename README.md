# nugbot

A Discord bot for the homies. Runs on a Raspberry Pi.

Built by [@jcacc](https://github.com/jcacc) and [@mulcare](https://github.com/mulcare).

## Commands

| Command | Description |
|---|---|
| `.drew [query]` | Returns a random quote from the Drew log, optionally filtered by a search term |
| `.gis <query>` | Google Image Search — returns an image URL |
| `.vampire [word]` | Returns a random line from the vampire flow, optionally filtered by a word |

## Setup

1. Clone the repo
2. Create a `config.yaml` from the template below
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python3 nugbot.py`

### config.yaml

```yaml
bot_token: YOUR_DISCORD_BOT_TOKEN
imagesearch:
  google_api_key: YOUR_GOOGLE_API_KEY
  search_engine_id: YOUR_SEARCH_ENGINE_ID
lastfm:
  api_key: YOUR_LASTFM_API_KEY
```

## Running as a service

A systemd service file is included. To install:

```bash
sudo cp nugbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nugbot
sudo systemctl start nugbot
```

## Version history

### 2026-02-20
- Migrated to discord.py 2.x
- Added `Intents` with `message_content` privilege
- All cog `setup()` functions and `load_nugs()` made async

### 2023–2024
- Initial build: drewbot, gis, vampire nugs
- Deployed to Raspberry Pi (lampPost) as a systemd service

## Structure

```
nugbot.py          # Bot entrypoint, loads nugs
config.yaml        # Secrets — gitignored, never commit
nugs/
  drewbot.py       # .drew command
  google.py        # .gis command
  vampire.py       # .vampire command
  lastfm.py        # .lastfm command (disabled)
```
