import datetime
import os
import sqlite3
import discord
from discord.ext import commands
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fm.db')


def _year_bounds(year: int):
    tz = datetime.timezone.utc
    start = int(datetime.datetime(year, 1, 1, tzinfo=tz).timestamp())
    end   = int(datetime.datetime(year + 1, 1, 1, tzinfo=tz).timestamp()) - 1
    return start, end


def _all_users():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute('SELECT discord_id, lastfm_username FROM users').fetchall()
    con.close()
    return rows


class Year(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _guild_lfm_users(self, guild):
        result = []
        for uid, lfm in _all_users():
            member = guild.get_member(int(uid))
            if not member:
                try:
                    member = await guild.fetch_member(int(uid))
                except Exception:
                    continue
            result.append((member, lfm))
        return result

    @commands.hybrid_command()
    async def year(self, ctx, year: Optional[int] = None):
        """Year in review — server-wide top artists, albums, tracks and listener stats."""
        if year is None:
            year = datetime.datetime.now(datetime.timezone.utc).year - 1

        start_ts, end_ts = _year_bounds(year)

        registered = await self._guild_lfm_users(ctx.guild)
        if not registered:
            await ctx.send('No registered Last.fm users in this server.')
            return

        lfm_names = [lfm for _, lfm in registered]
        ph = ','.join('?' * len(lfm_names))

        async with ctx.typing():
            con = sqlite3.connect(DB_PATH)

            total = con.execute(
                f'SELECT COUNT(*) FROM scrobbles WHERE lfm_username IN ({ph}) '
                f'AND scrobbled_at BETWEEN ? AND ?',
                lfm_names + [start_ts, end_ts]
            ).fetchone()[0]

            if total == 0:
                con.close()
                await ctx.send(f'No scrobbles cached for {year}. Try `.sync` first.')
                return

            top_artists = con.execute(
                f'SELECT artist, COUNT(*) as plays FROM scrobbles '
                f'WHERE lfm_username IN ({ph}) AND scrobbled_at BETWEEN ? AND ? '
                f'GROUP BY LOWER(artist) ORDER BY plays DESC LIMIT 5',
                lfm_names + [start_ts, end_ts]
            ).fetchall()

            top_albums = con.execute(
                f'SELECT album, artist, COUNT(*) as plays FROM scrobbles '
                f'WHERE lfm_username IN ({ph}) AND scrobbled_at BETWEEN ? AND ? '
                f'AND album != "" '
                f'GROUP BY LOWER(album), LOWER(artist) ORDER BY plays DESC LIMIT 5',
                lfm_names + [start_ts, end_ts]
            ).fetchall()

            top_tracks = con.execute(
                f'SELECT track, artist, COUNT(*) as plays FROM scrobbles '
                f'WHERE lfm_username IN ({ph}) AND scrobbled_at BETWEEN ? AND ? '
                f'GROUP BY LOWER(track), LOWER(artist) ORDER BY plays DESC LIMIT 5',
                lfm_names + [start_ts, end_ts]
            ).fetchall()

            top_listener = con.execute(
                f'SELECT lfm_username, COUNT(*) as plays FROM scrobbles '
                f'WHERE lfm_username IN ({ph}) AND scrobbled_at BETWEEN ? AND ? '
                f'GROUP BY lfm_username ORDER BY plays DESC LIMIT 1',
                lfm_names + [start_ts, end_ts]
            ).fetchone()

            user_top = []
            for member, lfm in registered:
                row = con.execute(
                    'SELECT artist, COUNT(*) as plays FROM scrobbles '
                    'WHERE lfm_username = ? AND scrobbled_at BETWEEN ? AND ? '
                    'GROUP BY LOWER(artist) ORDER BY plays DESC LIMIT 1',
                    (lfm, start_ts, end_ts)
                ).fetchone()
                if row:
                    user_top.append((member.display_name, row[0], row[1]))

            con.close()

        embed = discord.Embed(
            title=f'\U0001f3b5 {ctx.guild.name} \u2014 {year} in Review',
            description=f'**{total:,}** scrobbles across **{len(registered)}** listener{"s" if len(registered) != 1 else ""}',
            color=0xD51007
        )

        if top_artists:
            lines = [f'`{i+1}.` **{a}** \u2014 {p:,} plays' for i, (a, p) in enumerate(top_artists)]
            embed.add_field(name='Top Artists', value='\n'.join(lines), inline=False)

        if top_albums:
            lines = [f'`{i+1}.` **{alb}** \u2014 *{art}* \u2014 {p:,} plays' for i, (alb, art, p) in enumerate(top_albums)]
            embed.add_field(name='Top Albums', value='\n'.join(lines), inline=False)

        if top_tracks:
            lines = [f'`{i+1}.` **{t}** \u2014 *{art}* \u2014 {p:,} plays' for i, (t, art, p) in enumerate(top_tracks)]
            embed.add_field(name='Top Tracks', value='\n'.join(lines), inline=False)

        if top_listener:
            top_member = next((m for m, lfm in registered if lfm == top_listener[0]), None)
            top_name = top_member.display_name if top_member else top_listener[0]
            embed.add_field(
                name='Most Active Listener',
                value=f'**{top_name}** \u2014 {top_listener[1]:,} scrobbles',
                inline=False
            )

        if user_top:
            lines = [f'**{name}**: {artist} ({plays:,})' for name, artist, plays in user_top]
            embed.add_field(name='Personal Top Artist', value='\n'.join(lines), inline=False)

        embed.set_footer(text=f'Based on locally cached scrobbles \u00b7 Jan\u2013Dec {year}')
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Year(bot))
