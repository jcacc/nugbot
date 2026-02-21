import discord
from discord.ext import commands
import aiohttp
import json
import os
import yaml

LASTFM_API = 'https://ws.audioscrobbler.com/2.0/'
USERS_FILE = '/home/jca/nugbot/nugs/fm_users.json'

PERIODS = {
    'week':   '7day',
    'month':  '1month',
    '3month': '3month',
    '6month': '6month',
    'year':   '12month',
    'all':    'overall'
}


def load_config(config_file='./config.yaml'):
    with open(config_file) as f:
        return yaml.safe_load(f)


class FM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = load_config()
        self.api_key = config['lastfm']['api_key']
        self.users = self._load_users()

    def _load_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE) as f:
                return json.load(f)
        return {}

    def _save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f)

    def _get_lfm(self, user):
        return self.users.get(str(user.id))

    @commands.command()
    async def setfm(self, ctx, username: str):
        self.users[str(ctx.author.id)] = username
        self._save_users()
        await ctx.send(f'Last.fm username set to `{username}`.')

    @commands.command()
    async def fm(self, ctx, member: discord.Member = None):
        user = member or ctx.author
        lfm = self._get_lfm(user)
        if not lfm:
            await ctx.send('No Last.fm username set. Use `.setfm <username>`.')
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(LASTFM_API, params={
                'method': 'user.getrecenttracks',
                'user': lfm,
                'api_key': self.api_key,
                'format': 'json',
                'limit': 1
            }) as resp:
                data = await resp.json()

        tracks = data.get('recenttracks', {}).get('track', [])
        if not tracks:
            await ctx.send(f'No recent tracks found for `{lfm}`.')
            return

        track = tracks[0] if isinstance(tracks, list) else tracks
        now_playing = track.get('@attr', {}).get('nowplaying') == 'true'
        title   = track['name']
        artist  = track['artist']['#text']
        album   = track['album']['#text']
        url     = track['url']
        image   = next((i['#text'] for i in track.get('image', [])
                        if i['size'] == 'large' and i['#text']), None)

        embed = discord.Embed(
            title=title,
            url=url,
            description=f'by **{artist}**' + (f' on *{album}*' if album else ''),
            color=0xD51007
        )
        embed.set_author(name=f'{"🎵 Now playing" if now_playing else "⏮ Last played"} — {lfm}')
        if image:
            embed.set_thumbnail(url=image)

        await ctx.send(embed=embed)

    @commands.command()
    async def recent(self, ctx, member: discord.Member = None):
        user = member or ctx.author
        lfm = self._get_lfm(user)
        if not lfm:
            await ctx.send('No Last.fm username set. Use `.setfm <username>`.')
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(LASTFM_API, params={
                'method': 'user.getrecenttracks',
                'user': lfm,
                'api_key': self.api_key,
                'format': 'json',
                'limit': 5
            }) as resp:
                data = await resp.json()

        tracks = data.get('recenttracks', {}).get('track', [])
        if not tracks:
            await ctx.send(f'No recent tracks found for `{lfm}`.')
            return

        lines = []
        for t in tracks[:5]:
            now = t.get('@attr', {}).get('nowplaying') == 'true'
            lines.append(f'{"▶" if now else "·"} **{t["name"]}** — {t["artist"]["#text"]}')

        embed = discord.Embed(
            title=f'Recent tracks — {lfm}',
            description='\n'.join(lines),
            color=0xD51007
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def topartists(self, ctx, member_or_period: str = None, period_arg: str = None):
        member = None
        period_key = 'week'

        if member_or_period:
            try:
                member = await commands.MemberConverter().convert(ctx, member_or_period)
                if period_arg:
                    period_key = period_arg.lower()
            except commands.BadArgument:
                period_key = member_or_period.lower()

        user = member or ctx.author
        lfm = self._get_lfm(user)
        if not lfm:
            await ctx.send('No Last.fm username set. Use `.setfm <username>`.')
            return

        period = PERIODS.get(period_key, '7day')

        async with aiohttp.ClientSession() as session:
            async with session.get(LASTFM_API, params={
                'method': 'user.gettopartists',
                'user': lfm,
                'api_key': self.api_key,
                'format': 'json',
                'limit': 10,
                'period': period
            }) as resp:
                data = await resp.json()

        artists = data.get('topartists', {}).get('artist', [])
        if not artists:
            await ctx.send(f'No top artists found for `{lfm}`.')
            return

        lines = [f'`{i+1}.` **{a["name"]}** — {int(a["playcount"]):,} plays'
                 for i, a in enumerate(artists)]

        period_label = next((k for k, v in PERIODS.items() if v == period), period)
        embed = discord.Embed(
            title=f'Top artists ({period_label}) — {lfm}',
            description='\n'.join(lines),
            color=0xD51007
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FM(bot))
