import discord
from datetime import datetime
import asyncio
import difflib
import shlex

# ---------- STANDARDISED COLOURS ----------
blue = 0x89cff0
red = 0xcc0000
yellow = 0xffcc00
green = 0x66cc00
purple = 0x330099


# ---------- ROLES ----------
admin_roles = [167872530860867586, 167872106644635648]
reg_roles = [260945795744792578] + admin_roles

# ---------- FUNCTIONS ----------
async def is_admin(ctx):
    """
    Checks if user is an admin. This function is depreciated and will be removed in a future version.
    """
    roles = ctx.bot.config['admin_roles']

    for role_id in roles:
        test_role = discord.utils.get(ctx.guild.roles, id=role_id)
        if test_role in ctx.author.roles:
            return True
    return False

async def is_mod(ctx):
    """
    Checks if user is a mod. This function is depreciated and will be removed in a future version.
    """
    roles = ctx.bot.config['admin_roles'] + ctx.bot.config['mod_roles']

    for role_id in roles:
        test_role = discord.utils.get(ctx.guild.roles, id=role_id)
        if test_role in ctx.author.roles:
            return True
    return False

async def is_bot_channel(ctx):
    """
    Checks if command is in a bot channel
    """
    channel_list = ctx.bot.config['bot_channels']

    used_channel = ctx.channel.id
    for channel in channel_list:
        if channel == used_channel:
            return True
    # await ctx.send("Try this in a bot channel")
    return False

async def is_secret_channel(ctx):
    """
    Checks if command is a secret channel
    """
    channel_list = ctx.bot.config['secret_channels']

    used_channel = ctx.channel.id
    for channel in channel_list:
        if channel_list[channel] == used_channel:
            return True
    return False

async def bot_log(bot, log):
    """
    Logs bot activity
    """
    if bot.config['log_level'] in ("FULL", "CMD"):
        print(f"[!] {datetime.today()}: {log}")
    
    if bot.config['log_level'] == "FULL":
        channel = bot.get_channel(695039236117889054)
        await channel.send(f"{log}")

async def await_confirm(ctx, message, delete_after=True, confirm_time=10):
    '''
    Sends a message and waits for confirmation. 
    '''

    # SEND THE SUGGESTIONS
    sent_message = await ctx.send(message)

    # ADD THE CONFIRM EMOJI
    await sent_message.add_reaction('👍')

    # DEF CHECK OF RESPONSE
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == '👍'

    # AWAIT AND HANDLE RESPONSE
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=confirm_time, check=check)
        if delete_after:
            await sent_message.delete()
        else:
            await sent_message.edit(content=f"{message}\n`CONFIRMED`")
            await sent_message.clear_reactions()
        return True

    except asyncio.TimeoutError:
        # CLEAN UP
        if delete_after:
            await sent_message.delete()
        else:
            await sent_message.edit(content=f"{message}\n`CANCELLED`")
            await sent_message.clear_reactions()
        return False

async def await_react_confirm(confirm_message, bot, emoji='✅', confirm_time=60, delete_after=True):
    '''
    Reacts to a message and awaits a user to agree.
    '''

    # ADD THE CONFIRM EMOJI
    try:
        await confirm_message.add_reaction(emoji)
    except:
        return False, None

    # DEF CHECK FOR RESPONSE
    def check(reaction, user):
        return str(reaction.emoji) == emoji and user != bot.user and confirm_message.id == reaction.message.id

    # AWAIT AND HANDLE RESPONSE
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=confirm_time, check=check)
        if delete_after: await confirm_message.clear_reactions()
        return True, user
    except TimeoutError:
        if delete_after: await confirm_message.clear_reactions()
        return False, None

def close_match(search, possible_matches):
    '''
    Finds close string matches using difflib.get_close_matches
    '''

    possible_matches_lower = [i.lower() for i in possible_matches]

    search_lower = search.lower()

    try:
        solution = difflib.get_close_matches(search_lower, possible_matches_lower)

        index = possible_matches_lower.index(solution[0])

        upper_result = possible_matches[index]

        return upper_result
    
    except IndexError:
        return None

def sanitize_input(input_string):
    '''
    Removes tags commands etc from inputs. 
    '''
    output_str = input_string.replace('@&', '@&/')
    output_str = output_str.replace("@here", "@/here")
    output_str = output_str.replace("@everyone", "@/everyone")
    return(output_str)

def simple_parse(input_string, **kwargs):
    '''
    Parses arguments from a string.
    '''

    args = {}

    split_string = shlex.split(input_string)

    for k, v in kwargs.items():

        try:
            arg_index = split_string.index(f"-{v}")
            string_value = split_string[arg_index+1] 

            args[k] = string_value
            split_string.remove(f"-{v}")
            split_string.remove(string_value)

        except ValueError:
            args[k] = None
            continue
    
    trimmed_string = " ".join(split_string)
    return args, trimmed_string

def convert_to_number(input_var):
    try:
        output = float(input_var)
        return output
    except:
        return None