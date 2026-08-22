import sys

import discord
from discord.ext import commands
import requests
import yaml

# Console encoding on Windows defaults to the system codepage (e.g. cp1252),
# which can't print the non-BMP characters used below or in some nug output.
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def load_config(config_file = 'config.yaml'):
    with open(config_file) as file:
        config = yaml.safe_load(file)
    return config

CONFIG = load_config()

nugs = [
    'drewbot',
    'google',
    'vampire',
    'drewhal',
    'drewstats',
    # 'fm',
    'sysinfo',
    'speedtest',
    'youtube',
    'misquote'
]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

class Nugbot(commands.Bot):
    async def setup_hook(self):
        for nug in nugs:
            try:
                await self.load_extension(f'nugs.{nug}')
                print(f'[BOT] nug loaded successfully: {nug}')
            except Exception as e:
                print(f'[BOT] nug "{nug}" failed to load: {e}')
        await self.tree.sync()
        print('[BOT] slash commands synced')

bot = Nugbot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print('[BOT] 𝔫𝔲𝔤𝔟𝔬𝔱')
    print(f'[BOT] logged in as "{bot.user}"')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you 👀"))

bot.run(CONFIG['bot_token'])
