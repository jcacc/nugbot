import discord
from discord.ext import commands
import megahal
import random
import asyncio
import os

LOGFILE = '/home/jca/nugbot/nugs/drewzer0.txt'
BRAINFILE = '/home/jca/nugbot/nugs/drewhal.brain'
CHANNEL_ID = 177113512177303552

MIN_DELAY = 1 * 60    # 1 minute
MAX_DELAY = 15 * 60   # 15 minutes


class Drewhal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.hal = megahal.MegaHAL(brainfile=BRAINFILE)
        except Exception as e:
            print(f'[DREWHAL] Brain corrupted ({e}), deleting and retraining...')
            if os.path.exists(BRAINFILE + '.db'):
                os.remove(BRAINFILE + '.db')
            self.hal = megahal.MegaHAL(brainfile=BRAINFILE)
        self._train_task = None
        self._pending = None
        self._ready = False

    async def cog_load(self):
        self._train_task = asyncio.create_task(self._load_brain())

    def cog_unload(self):
        if self._train_task:
            self._train_task.cancel()
        if self._pending and not self._pending.done():
            self._pending.cancel()
        self.hal.close()

    async def _load_brain(self):
        await self.bot.wait_until_ready()
        if not os.path.exists(BRAINFILE + '.db'):
            print('[DREWHAL] No brain found — training from drewzer0.txt...')
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._train)
            self.hal.sync()
            print('[DREWHAL] Brain trained and saved.')
        else:
            print('[DREWHAL] Brain loaded.')
        self._ready = True

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

    async def _delayed_babble(self, seed, channel):
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(f'[DREWHAL] Babbling in {delay // 60}m {delay % 60}s')
        await asyncio.sleep(delay)
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, self.hal.get_reply_nolearn, seed)
        if reply:
            print(f'[DREWHAL] Babbling: {reply!r}')
            await channel.send(reply)
        self._pending = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != CHANNEL_ID:
            return
        if message.author.bot:
            return
        if not self._ready:
            return

        # Cancel any pending babble and reschedule
        if self._pending and not self._pending.done():
            self._pending.cancel()

        seed = message.content.strip() or 'hello'
        self._pending = asyncio.create_task(
            self._delayed_babble(seed, message.channel)
        )


async def setup(bot):
    await bot.add_cog(Drewhal(bot))
