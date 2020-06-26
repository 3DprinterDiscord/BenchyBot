import discord
from discord.ext import tasks, commands
import json
from git import Repo
import os
import bot_utils
import shutil
import git

class Wiki(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Wiki/config.json') as f:
            self.config_data = json.load(f)

        self.background_repo_update.start()

    @tasks.loop(hours=6)
    async def background_repo_update(self):
        # CREATE DIRECTORY
        try:
            os.mkdir('runtimefiles/wiki_repo')
        except FileExistsError:
            shutil.rmtree('runtimefiles/wiki_repo')
            os.mkdir('runtimefiles/wiki_repo')

        Repo.clone_from("https://github.com/3DprinterDiscord/wiki.wiki.git", "runtimefiles/wiki_repo")

        print("[!] Wiki Update Complete")

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def update_local_database(self, ctx):
        '''
        Updates the local copy of the wiki which is used for wiki commands.
        '''

        # CONFIRM
        if not await bot_utils.await_confirm(ctx, f"Confirm refresh of database. (This may take several seconds)", delete_after=False):
            return

        # CREATE DIRECTORY
        try:
            os.mkdir('runtimefiles/wiki_repo')
        except FileExistsError:
            shutil.rmtree('runtimefiles/wiki_repo')
            os.mkdir('runtimefiles/wiki_repo')

        Repo.clone_from("https://github.com/3DprinterDiscord/wiki.wiki.git", "runtimefiles/wiki_repo")

        await ctx.send("Done!")

    @commands.command()
    async def wiki(self, ctx, *, search_term=None):
        '''
        Used to search the wiki. Returns the best matched page and a link to it.
        '''

        if search_term == None:
            search_term = "Home"
        
        pages = [f.split(".")[0] for f in os.listdir('runtimefiles/wiki_repo') if str(f) != ".git"]

        found_page = bot_utils.close_match(search_term, pages)

        if found_page:
            f = open(f"runtimefiles/wiki_repo/{found_page}.md", "r")
            breif = f.readline()
            f.close()

            embed=discord.Embed(title=found_page.replace("-", " "), colour=bot_utils.blue)
            embed.add_field(name="Intro", value=breif.strip(), inline=False)
            embed.add_field(name="Source", value=f"https://github.com/3DprinterDiscord/wiki/wiki/{found_page}", inline=False)
            await ctx.send(embed=embed)

            # await ctx.send(f"Intro:\n```\n{breif.strip()}\n```Source: https://github.com/3DprinterDiscord/wiki/{found_page}")

def setup(bot):
    bot.add_cog(Wiki(bot))