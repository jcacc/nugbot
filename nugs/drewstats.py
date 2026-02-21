import discord
from discord.ext import commands
from collections import Counter
import re

LOGFILE = '/home/jca/nugbot/nugs/drewzer0.txt'

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'is', 'it', 'its', 'i', 'my', 'me', 'you', 'your', 'he',
    'she', 'we', 'they', 'that', 'this', 'was', 'are', 'be', 'been', 'have',
    'has', 'had', 'do', 'did', 'not', 'so', 'if', 'as', 'up', 'out', 'im',
    'its', 'like', 'just', 'get', 'got', 'dont', 'cant', 'all', 'from', 'what',
    'it', 'about', 'know', 'go', 'no', 'yeah', 'lol', 'yea', 'ok', 'okay'
}


class Drewstats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def drewstats(self, ctx):
        print(f'[DREWSTATS] invoked by {ctx.author}')
        try:
            async with ctx.typing():
                with open(LOGFILE, encoding='utf-8', errors='replace') as f:
                    lines = [l.strip() for l in f if l.strip()]

                total_lines = len(lines)
                all_words = []
                for line in lines:
                    words = re.findall(r"[a-zA-Z']+", line.lower())
                    all_words.extend(words)

                total_words = len(all_words)
                avg_len = sum(len(l) for l in lines) / total_lines
                longest = max(lines, key=len)

                filtered = [w for w in all_words if w not in STOPWORDS and len(w) > 2]
                top_words = Counter(filtered).most_common(10)
                top_str = '\n'.join(f'`{w}` — {c}' for w, c in top_words)

                embed = discord.Embed(
                    title='📊 drew stats',
                    color=0x8B1A1A
                )
                embed.add_field(name='Total lines', value=f'{total_lines:,}', inline=True)
                embed.add_field(name='Total words', value=f'{total_words:,}', inline=True)
                embed.add_field(name='Avg line length', value=f'{avg_len:.1f} chars', inline=True)
                embed.add_field(name='Top 10 words', value=top_str, inline=False)
                embed.add_field(
                    name='Longest line',
                    value=f'`{longest[:200]}{"..." if len(longest) > 200 else ""}`',
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            print(f'[DREWSTATS] error: {e}')
            await ctx.send(f'error: {e}')


async def setup(bot):
    await bot.add_cog(Drewstats(bot))
