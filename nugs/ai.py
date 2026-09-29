import os
import sqlite3
import discord
from discord.ext import commands
import anthropic
import yaml

NUGS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(NUGS_DIR, 'ai.db')

def load_config(config_file='config.yaml'):
    with open(config_file) as file:
        return yaml.safe_load(file)

CONFIG = load_config()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_facts (
            user_id INTEGER,
            fact TEXT,
            PRIMARY KEY (user_id, fact)
        )
    ''')
    conn.commit()
    return conn

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=CONFIG['anthropic']['api_key'])

    def get_facts(self, user_id):
        with get_db() as conn:
            rows = conn.execute(
                'SELECT fact FROM user_facts WHERE user_id = ?', (user_id,)
            ).fetchall()
        return [row[0] for row in rows]

    @commands.command(name='claude', help='Ask Claude something.')
    async def claude(self, ctx, *, prompt: str):
        facts = self.get_facts(ctx.author.id)
        system = None
        if facts:
            facts_list = '\n'.join(f'- {f}' for f in facts)
            system = f'Known facts about the user you are talking to:\n{facts_list}'

        async with ctx.typing():
            kwargs = dict(
                model='claude-opus-4-6',
                max_tokens=1024,
                messages=[{'role': 'user', 'content': prompt}]
            )
            if system:
                kwargs['system'] = system
            message = self.client.messages.create(**kwargs)
            response = message.content[0].text

        if len(response) <= 2000:
            await ctx.reply(response)
        else:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)

    @commands.command(name='airemember', help='Store a fact Claude will remember about you.')
    async def airemember(self, ctx, *, fact: str):
        with get_db() as conn:
            conn.execute(
                'INSERT OR IGNORE INTO user_facts (user_id, fact) VALUES (?, ?)',
                (ctx.author.id, fact)
            )
        await ctx.reply('Got it, I\'ll remember that.')

    @commands.command(name='aiforget', help='Clear all facts Claude knows about you.')
    async def aiforget(self, ctx):
        with get_db() as conn:
            conn.execute('DELETE FROM user_facts WHERE user_id = ?', (ctx.author.id,))
        await ctx.reply('Done, I\'ve forgotten everything about you.')

    @commands.command(name='aifacts', help='See what Claude knows about you.')
    async def aifacts(self, ctx):
        facts = self.get_facts(ctx.author.id)
        if not facts:
            await ctx.reply('I don\'t have any facts stored about you.')
        else:
            facts_list = '\n'.join(f'- {f}' for f in facts)
            await ctx.reply(f'Here\'s what I know about you:\n{facts_list}')

async def setup(bot):
    await bot.add_cog(AI(bot))
