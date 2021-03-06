import discord
from discord.ext import tasks, commands
import json
from git import Repo
import os
import bot_utils
import shutil
import git
from github import Github
import sqlite3

class Wiki(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Wiki/config.json') as f:
            self.config_data = json.load(f)

        self.background_repo_update.start()

        # LOAD ACCESS TOKEN
        try:
            token = open("modules/Wiki/token.txt", "r").read()
            print(f"   [✓] Github Token Read: {token}")
        except:
            print("    [✘] Token Read Failed. Please create token.txt in the Wiki module with your personal access token.")
            exit()

        self.g = Github(token)
        self.test_repo = self.g.get_repo('3DprinterDiscord/wiki')

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @tasks.loop(hours=6)
    async def background_repo_update(self):
        # CREATE DIRECTORY
        try:
            os.mkdir('runtimefiles/wiki_repo')
        except FileExistsError:
            shutil.rmtree('runtimefiles/wiki_repo')
            os.mkdir('runtimefiles/wiki_repo')

        Repo.clone_from("https://github.com/3DprinterDiscord/wiki.wiki.git", "runtimefiles/wiki_repo")

        # print("[!] Wiki Update Complete")

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def add_wiki_access(self, ctx, username=None):
        '''
        Adds a github account as a collaborator to the wiki so that you can edit pages. Please use this to add your own account only.
        '''

        if username==None:
            await ctx.send(f"Please use the format: `{self.bot.config['prefix']}add_wiki_access [github username]`")

        try:
            self.test_repo.add_to_collaborators(username)
            await ctx.send("Done!")
        except:
            await ctx.send("Failed! Make sure you are using your github username and it is spelt correctly.")
            return

        self.c.execute("INSERT INTO Wiki (discord_name, github_name) VALUES (?, ?)", (str(ctx.author), username))
        self.conn.commit()

    def get_username(self, member):
        self.c.execute("SELECT * FROM Wiki WHERE discord_name=?", (str(member), ))
        result = self.c.fetchall()
        return result

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def wiki_gen_commands_page(self, ctx):
        '''Generates the bot commands page [Beta]'''
        self.c.execute("SELECT * FROM Commands WHERE command_type=?", ('help', ))
        results = self.c.fetchall()

        output_list = [f"### {i[0]}\n{i[1]}\n\n" for i in results]

        output_list = ["This page echos the help commands currently loaded onto the bot. You can summon these commands with using the `?` prefix. This list will be updated periodically.\n\n## Commands\n"] + output_list

        f = open("test_output.txt", "w")
        f.writelines(output_list)
        f.close()

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def wiki_info(self, ctx):
        '''Displays Wiki Info. [beta]'''
        files = os.listdir("runtimefiles/wiki_repo")
        files = [i for i in files if not i.startswith('_')]

        embed=discord.Embed(title='Wiki Info', colour=bot_utils.blue)
        embed.add_field(name="Pages", value=len(files), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def wiki_who(self, ctx, username=None):
        '''Displays discord users github names.'''
        # GET DATABASE RESULTS
        self.c.execute("SELECT * FROM Wiki")
        result = self.c.fetchall()

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- WIKI USERNAMES ({len(result)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for command in result:
            paginator.add_line(f"{command[0]} : {command[1]}")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page, delete_after=60)
        
    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
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
            embed.add_field(name="Continue Reading...", value=f"https://github.com/3DprinterDiscord/wiki/wiki/{found_page}", inline=False)
            await ctx.send(embed=embed)

        else:
            embed=discord.Embed(title="Page Not Found", description="That page wasnt found! Try browsing the wiki and using the page search on the right hand side.", colour=bot_utils.blue)
            embed.add_field(name="Homepage", value="[Homepage Link](https://github.com/3DprinterDiscord/wiki/wiki)", inline=False)
            await ctx.send(embed=embed)


    def cog_unload():
        self.background_repo_update.stop()

def setup(bot):
    bot.add_cog(Wiki(bot))