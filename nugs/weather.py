import discord
from discord.ext import commands
import requests

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wx')
    async def wx(self, ctx, zipcode: str = None):
        if not zipcode:
            await ctx.send('Usage: `.wx <zipcode>`')
            return

        try:
            response = requests.get(
                f'https://wttr.in/{zipcode}',
                params={'format': '3'},
                timeout=5
            )
            response.raise_for_status()
            await ctx.send(response.text.strip())
            print(f'[WEATHER] {ctx.author} requested weather for {zipcode}')
        except requests.exceptions.Timeout:
            await ctx.send('Weather service timed out, try again.')
        except Exception as e:
            await ctx.send('Could not retrieve weather.')
            print(f'[WEATHER] Error for {zipcode}: {e}')

async def setup(bot):
    await bot.add_cog(Weather(bot))
