import discord
from discord.ext import commands
import json
import bot_utils
import sqlite3

class Blacklist(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Blacklist/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):
        self.c.execute("SELECT * FROM Blacklist")
        banned_terms = self.c.fetchall()

        # Delete messages
        if message.author != self.bot.user:
            for s in banned_terms:
                if s[0] in message.content.lower():
                    await message.delete()

                    if self.config_data["blacklist_message"] != "":
                        await message.author.send(self.config_data["blacklist_message"])

                    await bot_utils.bot_log(self.bot, f"'Message removed: '{message.content}' by {message.author}")

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def add_banned_term(self, ctx, term):
        """Adds blacklisted terms to the database"""
        term = term.lower()

        print(f"[!] Adding {term} to databse!")

        try:
            self.c.execute("INSERT INTO Blacklist(term) VALUES (?)", (term,))
            self.conn.commit()
            await ctx.send(f"'{term}' added to blacklist!")
            await bot_utils.bot_log(self.bot, f"'Blacklist term '{term}' added by {ctx.message.author}")
        except:
            await ctx.send(f"'{term}' failed to add to blacklist!")

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def remove_banned_term(self, ctx, term):
        """Adds blacklisted terms to the database"""
        print(f"[!] Removing {term} from databse!")
        # Load blacklist terms
        try:
            self.c.execute("DELETE FROM Blacklist WHERE term=?", (term,))
            self.conn.commit() 
            await ctx.send(f"'{term}' removed from blacklist!")
            await bot_utils.bot_log(self.bot, f"'Blacklist term {term} removed by {ctx.message.author}")
        except:
            await ctx.send(f"'{term}' failed to remove from blacklist!")

    @commands.command(hidden=True)
    @commands.check(bot_utils.is_admin)
    async def view_banned_terms(self, ctx):
        self.c.execute(f"SELECT * FROM Blacklist")
        banned_terms = self.c.fetchall()

        terms = "\n".join(str(t[0]) for t in banned_terms)

        embed = discord.Embed(title="Banned Terms", description=terms, color=bot_utils.red)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Blacklist(bot))