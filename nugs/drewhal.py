import discord
from discord.ext import commands
import megahal
import random
import asyncio
import os

LOGFILE = '/home/jca/nugbot/nugs/drewzer0.txt'
BRAINFILE = '/home/jca/nugbot/nugs/drewhal.brain'
CHANNEL_ID = 177113512177303552

MIN_DELAY = 30 * 60    # 30 minutes
MAX_DELAY = 3 * 60 * 60  # 3 hours


class Drewhal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hal = megahal.MegaHAL(brainfile=BRAINFILE)
        self._task = None

    async def cog_load(self):
        # Kick off as a background task so setup_hook isn't blocked during training
        self._task = asyncio.create_task(self._babble_loop())

    def cog_unload(self):
        if self._task:
            self._task.cancel()
        self.hal.close()

    async def _babble_loop(self):
        await self.bot.wait_until_ready()
        if not os.path.exists(BRAINFILE):
            print('[DREWHAL] No brain found — training from drewzer0.txt...')
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._train)
            self.hal.sync()
            print('[DREWHAL] Brain trained and saved.')
        else:
            print('[DREWHAL] Brain loaded.')
        while not self.bot.is_closed():
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f'[DREWHAL] Next babble in {delay // 60}m')
            await asyncio.sleep(delay)
            channel = self.bot.get_channel(CHANNEL_ID)
            if not channel:
                print(f'[DREWHAL] Channel {CHANNEL_ID} not found')
                continue
            with open(LOGFILE, encoding='utf-8', errors='replace') as f:
                lines = [l.strip() for l in f if l.strip()]
            seed = random.choice(lines)
            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(None, self.hal.get_reply_nolearn, seed)
            if reply:
                print(f'[DREWHAL] Babbling: {reply!r}')
                await channel.send(reply)

    def _train(self):
        with open(LOGFILE, encoding='utf-8', errors='replace') as f:
            lines = [l.strip() for l in f if l.strip()]
        total = len(lines)
        skipped = 0
        for i, line in enumerate(lines):
            try:
                self.hal.learn(line)
            except Exception:
                skipped += 1
                continue
            pct = int((i + 1) / total * 100)
            if pct % 10 == 0 and int(i / total * 100) != pct:
                print(f'[DREWHAL] Training: {pct}%')
        print(f'[DREWHAL] Training complete. Skipped {skipped} bad lines.')


async def setup(bot):
    await bot.add_cog(Drewhal(bot))
