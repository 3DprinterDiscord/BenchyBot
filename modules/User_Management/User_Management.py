import discord
from discord.ext import commands, tasks
import json
import bot_utils
import datetime
from matplotlib import pyplot as plt
import sqlite3

class User_Management(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/User_Management/config.json') as f:
            self.config_data = json.load(f)

        # START BACKGROUND TASKS
        if self.config_data['activity_check'] != 0:
            self.user_activity_check.start()

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(member)
        # ADD SOME STUFF HERE 

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # get channel membership_channel
        print(member)
        # send left message

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def membership_info(self, ctx):
        '''
        Gets info on the server membership.
        '''

        async with ctx.typing():

            # GET MEMEBRS LIST
            members = ctx.guild.members

            # CREATE EMBED
            embed = discord.Embed(title=f"Membership Info", description=f"Membership info for {ctx.guild}", color=bot_utils.green)

            embed.add_field(name="Total Members:", value=len(members), inline=True)

            embed.add_field(name="Online:", value=len([member for member in members if member.status == discord.Status.online]), inline=True)

            embed.add_field(name="Roles:", value=len(ctx.guild.roles), inline=True)

            embed.add_field(name="Channels:", value=len(ctx.guild.channels), inline=True)

            ### --- USER GROWTH --- ###

            # ORDER MEMEBERS
            ordered_members = sorted(members, key=lambda r: r.joined_at)

            # GENERATE USER GRAPH DATA 
            i = 0
            x_data = []
            y_data = []

            for member in ordered_members:
                i = i + 1
                x_data.append(member.joined_at)
                y_data.append(i)

            # PLOT AND SET TITLES 
            plt.plot(x_data,y_data, color="black")
            plt.xlabel('Date')
            plt.ylabel('Users')
            plt.title('User Growth')

            # SAVE IMAGE
            plt.savefig('runtimefiles/user_graph.png')
            plt.clf() 

            ### --- USER ACTIVITY --- ###

            # GET ACTIVITY NUMBERS
            self.c.execute("SELECT * FROM User_Activity")
            user_activity = self.c.fetchall()

            trimmed_data = user_activity[:672]

            x_data = [datetime.datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S.%f') for d in trimmed_data]
            y_data = [int(d[1]) for d in trimmed_data]

            # PLOT AND SET TITLES 
            plt.plot(x_data,y_data, color="black")
            plt.xlabel('Date')
            plt.ylabel('Active Users')
            plt.title('7-Day User Activity')

            # SAVE IMAGE
            plt.savefig('runtimefiles/user_activity.png')
            plt.clf() 

            ### --- SEND OBJECTS --- ###

            # SEND EMBED
            await ctx.send(embed=embed)

            # LOAD DISCORD FILE
            loaded_file_1 = discord.File("runtimefiles/user_graph.png", filename="image1.png")
            loaded_file_2 = discord.File("runtimefiles/user_activity.png", filename="image2.png")

            # SEND GRAPH
            await ctx.send(file=loaded_file_1)
            await ctx.send(file=loaded_file_2)

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def user_info(self, ctx, username):
        '''
        Gets info on a user
        '''

        # GET MEMEBER
        member = discord.utils.find(lambda m: username.lower() in m.name.lower(), ctx.guild.members)

        # CHECK MEMBER EXISTS
        if member is None:
            await ctx.send("Member Not Found.")
            return

        # EMBED
        embed = discord.Embed(title=f"User Info For {member}", description=f"Display Name: {member.display_name}", color=bot_utils.green)

        # JOIN DATE
        days = str(datetime.datetime.utcnow() - member.created_at).split(" ")[0]
        created_string = f"{member.created_at.strftime('%Y-%m-%d')} ({days} days)"
        embed.add_field(name="Joined Discord on:", value=created_string, inline=False)

        # JOINED DISCORD
        days = str(datetime.datetime.utcnow() - member.joined_at).split(" ")[0]
        joined_string = f"{member.joined_at.strftime('%Y-%m-%d')} ({days} days)"
        embed.add_field(name="Joined Server on:", value=joined_string, inline=False)

        # NITRO SINCE
        if not member.premium_since is None:
            nitro_days = str(datetime.datetime.utcnow() - member.premium_since).split(" ")[0]
            nitro_string = f"{member.premium_since.strftime('%Y-%m-%d')} ({days} days)"
        else:
            nitro_string = "Not Boosting"
        embed.add_field(name="Nitro Since:", value=nitro_string, inline=False)

        # CURRENT STATUS
        embed.add_field(name="Current Status:", value=member.status, inline=False)

        # CONNECTION STATUS
        is_mobile = member.is_on_mobile()
        embed.add_field(name="On Mobile?", value=is_mobile, inline=False)

        # ROLES
        embed.add_field(name="Roles:", value=", ".join([i.name for i in member.roles]), inline=True)

        await ctx.send(embed=embed)

    @tasks.loop(minutes=15)
    # @tasks.loop(seconds=5)
    async def user_activity_check(self):

        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        members = self.bot.get_guild(self.config_data['guild_id']).members 

        online_members = len([member for member in members if member.status == discord.Status.online])

        self.c.execute("INSERT INTO User_Activity(time_stamp, online) VALUES (?, ?)", (datetime.datetime.utcnow(), online_members))
        self.conn.commit()

def setup(bot):
    bot.add_cog(User_Management(bot))