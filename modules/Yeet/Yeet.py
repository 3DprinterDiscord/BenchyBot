
import discord
from discord.ext import commands
import json
import asyncio
import random
import bot_utils
import re

COMBO = '''
   _____                _           _ 
  / ____|              | |         | |
 | |     ___  _ __ ___ | |__   ___ | |
 | |    / _ \| '_ ` _ \| '_ \ / _ \| |
 | |___| (_) | | | | | | |_) | (_) |_|
  \_____\___/|_| |_| |_|_.__/ \___/(_)
  '''

class Yeet(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Yeet/config.json') as f:
        #     self.config_data = json.load(f)

        self.yeets = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 730178093444104272:
            if message.author.id == self.bot.user.id:
                return

            x = re.findall('(Y|y)(e|E){2,}(T|t)', message.content)
            if x:
                print("yeet")
                await message.add_reaction(":yeet:730210956793086034")
                self.yeets = self.yeets + len(x)
                if len(x) > 1:
                    await message.channel.send(f"```{COMBO}```")
            else:
                print("not a yeet")
                await message.channel.send('GTFO.')

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def yeet(self, ctx):
        '''
        Shows yeet count.
        '''
        
        await ctx.send(f"Thats {self.yeets} yeets!")

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def unyeet(self, ctx):
        '''
        Resets Yeet count.
        '''
        await ctx.send(f"Thats {self.yeets} yeets set back to 0 yeets all thanks to {ctx.author.name}!")
        self.yeets = 0


def setup(bot):
    bot.add_cog(Yeet(bot))