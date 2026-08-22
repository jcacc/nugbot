import discord
from discord.ext import commands
import anthropic
import random
import re
import yaml

def load_config(config_file='config.yaml'):
    with open(config_file) as file:
        return yaml.safe_load(file)

CONFIG = load_config()

class Misquote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=CONFIG['anthropic']['api_key'])

    @commands.command(name='misquote', help='Subtly misquote someone. Add -unhinged for chaos.')
    async def misquote(self, ctx, member: discord.Member, flag: str = None):
        # Grab recent messages from this user across channels in the guild
        messages = []
        for channel in ctx.guild.text_channels:
            try:
                async for msg in channel.history(limit=200):
                    if msg.author.id == member.id and not msg.author.bot and len(msg.content) > 15 and not re.search(r'https?://', msg.content):
                        messages.append(msg.content)
                    if len(messages) >= 50:
                        break
            except discord.Forbidden:
                continue
            if len(messages) >= 50:
                break

        if not messages:
            await ctx.reply(f'Couldn\'t find any messages from {member.display_name}.')
            return

        # Weight older messages more heavily (index 0 = newest, last = oldest)
        weights = [i + 1 for i in range(len(messages))]
        original = random.choices(messages, weights=weights, k=1)[0]

        unhinged = flag and flag.lower() in ('-unhinged', 'unhinged')
        if unhinged:
            system = 'You are an unhinged misquote machine. You receive a quote and return a wildly altered version. Keep the general topic but make it absurd, deranged, or hilariously wrong. Go completely off the rails. Output ONLY the altered quote. No commentary, no preamble, no explanation, no thinking, no meta-text. Just the altered quote and nothing else.'
        else:
            system = 'You are a misquote machine. You receive a quote and return a subtly altered version. Change a few words to make it slightly wrong, weird, or embarrassing — but keep it believable. Keep the same length and tone. Output ONLY the altered quote. No commentary, no preamble, no explanation, no thinking, no meta-text. Just the altered quote and nothing else.'

        async with ctx.typing():
            response = self.client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=256,
                system=system,
                messages=[{'role': 'user', 'content': original}]
            )
            misquoted = response.content[0].text

        await ctx.send(f'> {misquoted}\n— {member.display_name}')

async def setup(bot):
    await bot.add_cog(Misquote(bot))
