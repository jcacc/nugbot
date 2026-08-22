import discord
from discord.ext import commands
import subprocess
import re
import socket

OWNER_ID = 260481053913907200


class Speedtest(commands.Cog):
    @commands.hybrid_command()
    async def speedtest(self, ctx):
        """Run a network speed test."""
        if ctx.author.id != OWNER_ID:
            await ctx.send('nope', ephemeral=True)
            return

        msg = await ctx.send('Running speed test, this takes ~30 seconds...')
        try:
            result = subprocess.run(
                ['speedtest-cli', '--simple'],
                capture_output=True, text=True, timeout=120
            )
            output = result.stdout.strip()
            if not output:
                await msg.edit(content=f'Speed test failed: {result.stderr.strip()}')
                return

            # Parse: Ping: X ms / Download: X Mbit/s / Upload: X Mbit/s
            ping = re.search(r'Ping:\s+([\d.]+)', output)
            download = re.search(r'Download:\s+([\d.]+)', output)
            upload = re.search(r'Upload:\s+([\d.]+)', output)

            embed = discord.Embed(title=f'🌐 Speed test — {socket.gethostname()}', color=0x3498db)
            if ping:
                embed.add_field(name='Ping', value=f'{ping.group(1)} ms', inline=True)
            if download:
                embed.add_field(name='Download', value=f'{download.group(1)} Mbit/s', inline=True)
            if upload:
                embed.add_field(name='Upload', value=f'{upload.group(1)} Mbit/s', inline=True)

            await msg.edit(content=None, embed=embed)
        except FileNotFoundError:
            await msg.edit(content=f'`speedtest-cli` is not installed on {socket.gethostname()}. Run `pip3 install speedtest-cli`.')
        except subprocess.TimeoutExpired:
            await msg.edit(content='Speed test timed out.')


async def setup(bot):
    await bot.add_cog(Speedtest())
