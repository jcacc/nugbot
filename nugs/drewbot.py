import discord
from discord.ext import commands
from random import choice, randint
import linecache

LOGFILE = '/home/jca/nugbot/nugs/drewzer0.txt'

class Drewbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def drew(self, ctx, *, query: str = ''):
        print(f"[DREWBOT] invoked by {ctx.author} with query: {query!r}")
        lines = await self.query_lines(query)

        if query and not lines:
            await ctx.send(f'No matches for “{query}”.')
            print(f"[DREWBOT] 0 matches for {query!r}")
            return

        if not query and not lines:
            await ctx.send('No lines in the database yet.')
            print("[DREWBOT] Log empty.")
            return

        drewsay = self.random_line(lines)
        await ctx.send(drewsay)

        if not query:
            print(f'[DREWBOT] {ctx.author} asked for random drewsay')
        else:
            print(f'[DREWBOT] {ctx.author} asked for drewsay including {query!r}')
        print(f'[DREWBOT] ↳ returned: {drewsay!r}')

    async def query_lines(self, query: str):
        drew_lines = []
        with open(LOGFILE, encoding='utf-8', errors='replace') as f:
            for line in f:
                text = line.rstrip('\n')
                if not text:
                    continue
                if not query or query.casefold() in text.casefold():
                    drew_lines.append(text)
        print(f"[DREWBOT] query_lines -> {len(drew_lines)} lines (query={query!r})")
        return drew_lines

# With a populated list of lines, select a random line and return it. If
# the list is empty, it is because the call to the bot was submitted
# without a string to look for in the log, or there was no match in the
# log for the submitted string. In that case, we can populate the list
# with lines of a random minimum length (which gives some variation and
# helps avoid the overrepresented relatively short lines), and select
# one line randomly from that list.

    def random_line(self, drew_lines):
        if not drew_lines:
            drew_lines = self.lines_of_random_length()
        return choice(drew_lines).strip()


    def lines_of_random_length(self):
        drew_lines = []
        line_length = randint(1, 100)
        with open(LOGFILE) as f:
            for line in f:
                if len(line) >= line_length:
                    drew_lines.append(line)
        return drew_lines
                
# Full lines from chat log contain a timestamp, nick string, and chat
# text string, each separated by a tab (\t). Each line ends with a
# newline (\n). We want to return only the chat text string, so need to
# clean the selected line accordingly.

    def clean_line(self, line):
        line = line.split('\t')[2].removesuffix('\n')
        return line

def setup(bot):
    bot.add_cog(Drewbot(bot))