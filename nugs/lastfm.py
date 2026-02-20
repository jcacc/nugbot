import discord
from discord.ext import commands
import yaml
import requests
import json
import urllib.request

def load_config(config_file = './config.yaml'):
    with open(config_file) as file:
        config = yaml.safe_load(file)
    return config

CONFIG = load_config()

class Lastfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lastfm(self, ctx, username):
        track = await self.get_last_track(username)
        print(f'{ctx.author} ({username}) scrobbled: {track}')
        await ctx.send(track)

    async def call_lastfm_api(self, args):
        api_key = CONFIG['lastfm']['api_key']
        api_url = f'http://ws.audioscrobbler.com/2.0/?&format=json&api_key={api_key}'

        for key, value in args.items():
            api_url += f'&{key}={value}'

        uri = urllib.request.urlopen(f'{api_url}')
        track = json.loads(uri.read().decode())
        return track['recenttracks']['track']

    async def get_last_track(self, username):
        last_track = await self.call_lastfm_api(
            {
                'method': 'user.getrecenttracks',
                'user': username,
                'limit': '1'
            }
        )

        track_name = last_track[0]['name']
        track_mbid = last_track[0]['mbid']
        artist_name = last_track[0]['artist']['#text']
        album_name = last_track[0]['album']['#text']

        return f'♫ **{track_name}** by **{artist_name}** on **{album_name}**'

def setup(bot):
    bot.add_cog(Lastfm(bot))