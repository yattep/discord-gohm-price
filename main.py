### imports
import os
import time
import discord
from discord.ext import commands
from discord.ext import tasks
import json
from pycoingecko import CoinGeckoAPI
import traceback
import constants
import asyncio
import gohmpricebot
import ohmpricebot
import ohmindexbot
import ohmlbbot
from helpers import get_circulating_supply, get_price_ohm, get_price_gohm, get_raw_index, get_7d_lb_sma, get_7d_floating_supply, get_7d_agg_token_values, get_7d_lb_sma_raw, get_current_day_lb, human_format, get_image_data

gpb = gohmpricebot.GohmPriceDiscordBot("olyprice!",constants.ADMIN_ROLE, constants.PRICE_UPDATE_INTERVAL)

opb = ohmpricebot.OhmPriceDiscordBot("ohmprice!",constants.ADMIN_ROLE, constants.PRICE_UPDATE_INTERVAL)

oib = ohmindexbot.OhmIndexDiscordBot("olyindex!",constants.ADMIN_ROLE, constants.GENERIC_UPDATE_INTERVAL)

olbb = ohmlbbot.OhmLiquidBackingDiscordBot("ohmliq!",constants.ADMIN_ROLE, constants.LB_UPDATE_INTERVAL)

###OHM MCAP BOT START###
mcap_bot = commands.Bot(command_prefix="olymcap!")
LAST_VAL = ''
### log in
@mcap_bot.event
async def on_ready():
    print(f"Logged in as {mcap_bot.user.name}")
    print("------")
    if update_mcap.is_running():
      print("Task Already Running on_ready")
    else:
      await update_mcap.start()  # DYNAMIC

@mcap_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    for guild in mcap_bot.guilds:
        await mcap_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"OHM MCAP"))
    await ctx.send("Yes ser, on it boss.")

@mcap_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def forceupdate(ctx):
    await ctx.send("Yes ser, on it boss.")
    newName = get_ohm_mcap()
    for guild in mcap_bot.guilds:
        await guild.me.edit(nick=newName)
        await mcap_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"OHM MCAP"))
    await ctx.send("Happy to report it has been updated!")

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.GENERIC_UPDATE_INTERVAL)
async def update_mcap():
    try:
        newName = await get_ohm_mcap()
        print(f"Updating nickname to: {newName}")
        ## dynamic updates
        for guild in mcap_bot.guilds:
            await guild.me.edit(nick=newName)
            await mcap_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM MCAP"))
    except:
        print("likely discord rate limit")

async def get_ohm_mcap():
    global LAST_VAL
    try:
      price = get_price_ohm()
      circ_supply = get_circulating_supply()
      mcap = price * circ_supply
      name_val = human_format(float(mcap))
      LAST_VAL = name_val
      return name_val
    except:
      traceback.print_exc()
      print("subgraph exception")
      return LAST_VAL
###OHM MCAP BOT END###

###SENTINEL BOT START###
### intents
intents = discord.Intents.default()  # allows the use of custom intents
intents.members = True  # allows to pull member roles among other things
intents.presences = True
discord.MemberCacheFlags.none
sentinel_bot = commands.Bot(command_prefix="oly!", intents=intents)
### log in
@sentinel_bot.event
async def on_ready():
    print(f"Logged in as {sentinel_bot.user.name}")
    print("------")

### role kicker
@sentinel_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)  # requires user to have this role
async def masskick(ctx, role: discord.Role):

    total = len(role.members)
    kicked = 0

    await ctx.message.add_reaction('🧠')  # lets user know command is processing

    print(f"queued for kick: {total}")  #console
    for member in role.members:
        await ctx.guild.kick(member)
        await ctx.channel.send(
            f"[{kicked}/{total}] kicked: {member.name} | <@{member.id}>"
        )  # discord
        print(
            f"[{kicked}/{len(role.members)}] kicked: {member.name} | <@{member.id}>"
        )  # console
        kicked += 1  #increment
        await asyncio.sleep(1)  # sleep call between interactions to avoid 429 rate limit

    await ctx.message.clear_reaction('🧠')  # remove processing reaction
    await ctx.message.add_reaction('✅')  # add finished reaction
    time.sleep(1)
    await ctx.message.reply(f"kicked {total} users in given role.")  # let user know

### lets you know how many users exist in a role
@sentinel_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)  # requires user to have this role
async def listzero(ctx, role: discord.Role):
    
    members = filter(lambda m: len(m.roles) == 1, role.members)
    try:
      await ctx.send(" ".join(str(member.id) for member in members))
    except:
      await ctx.send("No members found")

### lets you know how many users exist in a role
@sentinel_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)  # requires user to have this role
async def bulkrole(ctx, role: discord.Role, *users):
    guild = sentinel_bot.get_guild(ctx.guild.id)
    count = 0
    await ctx.message.add_reaction('🧠')  # lets user know command is processing
    for user in users:
        try:
          member = await guild.fetch_member(user)
          await member.add_roles(role)
          count += 1
        except:
          pass
        await asyncio.sleep(1)

    await ctx.message.add_reaction('✅')  # add finished reaction
  
    await ctx.send("Added {} to {} users".format(role,count))

### Bot function #1
# DM new grasshoppers, if they have DM open they will get this message
@sentinel_bot.event
async def on_member_update(before, after):
    #member = bot.get_guild(before.guild.id).get_member(before.id)

    guild = sentinel_bot.get_guild(before.guild.id)
    
    g_role = discord.utils.get(guild.roles, name=constants.GRASSHOPPER) # role object for grasshoppers
    
    if (g_role not in before.roles
            and g_role in after.roles):
        print(f"detected new grasshopper, {after.name}|{after.id}") #CONSOLE LOGGING
        #LOGGING OUTPUT
        channel = sentinel_bot.get_channel(constants.LOG_CHANNEL)
        await channel.send(
            f"Notifying new grasshopper to disable DMs, {after.name} | {after.id}")
        #NOTIFY USER VIA DM      
        try:
          await after.send(
              "**WARNING:**\n\nYou recently opened Direct Messages from server members and are vulnerable to DM scams until you disable direct messages from server members.\n\nThis is the most common attack vector and is easily mitigated. \n\nPlease go to the server settings and uncheck **Allow direct messages from server members**. Stay safe!")
        except:
          print(f"Could not DM: {after.name} | {after.id}")
        await asyncio.sleep(30)
        #WELCOME USER IN GENERAL
        genChannel = sentinel_bot.get_channel(constants.GENERAL_CHANNEL)
        await genChannel.send(
            f"Welcome young grasshopper <@{after.id}>, it's great to have you here.\n\nTell us a little about yourself and what brings you to Olympus!", delete_after=constants.EXPIRATION)
        await asyncio.sleep(90)
        #INTRODUCE USER IN LEARN
        learn = sentinel_bot.get_channel(constants.LEARN_CHANNEL)
        await learn.send(
            f"Once you've had a chance to introduce yourself in <#{constants.GENERAL_CHANNEL}>, <@{after.id}>, be sure to check out this channel and ask any of those burning questions you might have!\n\nAlso check out the top of the channels list to RSVP for any of this week's events.", delete_after=constants.EXPIRATION)
        #await asyncio.sleep(90)
        #INTRODUCE USER IN OT
        #ot = bot.get_channel(OT_CHANNEL)
        #await ot.send(
        #    f"Looking to blow off some steam or connect with other Ohmies <@{after.id}>? <#{OT_CHANNEL}> is not for the faint of heart, do you have what it takes?", delete_after=EXPIRATION)
        await asyncio.sleep(90)
        await genChannel.send(f"<@{after.id}>, Do you hold sOHM or gOHM? Check out <#981648330822152333> to verify your assets to gain the exclusive `Ohmies (Verified)` role!", delete_after=constants.EXPIRATION)

### Bot function #2
# check for role assignment, kick after X seconds if no roles selected
@sentinel_bot.event
async def on_member_join(member):
    
    await asyncio.sleep(360)
    
    guild = sentinel_bot.get_guild(member.guild.id)
    e_role = discord.utils.get(guild.roles, name="@everyone")
    #use fetch_member because get_member pulls from cache
    try:
        member_check = await guild.fetch_member(member.id)
    except:
        member_check = None
        print(f"Couldn't locate member {member.id} | {member.name}")
    if member_check:
        if (len(member_check.roles) == 1 and e_role in member_check.roles):
             print(f"Kicking, {member_check.name} | {member_check.id}")
             print("------")
             channel = sentinel_bot.get_channel(constants.LOG_CHANNEL)
             await channel.send(
                f"Notified and kicked user that verified and selected no roles, {member_check.name}|{member_check.id}")
             try:
                await member_check.send(
               f"You have been kicked from {guild.name} because you did not assign roles within 6 minutes of joining the server, please rejoin and select roles to avoid being kicked.")
             except:
                pass
    
             await guild.kick(member_check)

### Bot function #3
# have some fun

# Set the threshold for detecting a streak
streak_threshold = 3

# Initialize variables to track the streak
streak_message = None
streak_count = 0
streak_users = []
sequence_position = 0

# Define a function to add the appropriate number of reaction emojis
async def add_reactions(message, count=None):
    try:
        if count is None:
            # If the count is equal to the threshold, add a green checkmark emoji
            if streak_count == streak_threshold:
                await message.add_reaction(u"\u2705")  # Green checkmark emoji
            # If the count is less than or equal to 9, add the corresponding number emoji
            elif streak_count <= 9:
                await message.add_reaction(str(streak_count) + u"\u20e3")
            # If the count is 33, add the custom :33: reaction
            elif streak_count == 33:
                await message.add_reaction(":33:")
            # If the count is greater than 9, add the tens and ones digit emojis
            else:
                tens_digit = streak_count // 10
                ones_digit = streak_count % 10
                await message.add_reaction(str(tens_digit) + u"\u20e3")
                await message.add_reaction(str(ones_digit) + u"\u20e3")
        else:
            # If the count is less than or equal to 9, add the corresponding number emoji
            if count <= 9:
                await message.add_reaction(str(count) + u"\u20e3")
            # If the count is 33, add the custom :33: reaction
            elif count == 33:
                await message.add_reaction(":33:")
            # If the count is greater than 9, add the tens and ones digit emojis
            else:
                tens_digit = count // 10
                ones_digit = count % 10
                await message.add_reaction(str(tens_digit) + u"\u20e3")
                await message.add_reaction(str(ones_digit) + u"\u20e3")
    except Exception as e:
        print(f"Error adding reactions: {e}")


# Define a function to reset the streak variables
def reset_streak():
    global streak_message, streak_count, streak_users, sequence_position
    streak_message = None
    streak_count = 0
    streak_users = []
    sequence_position = 0

@sentinel_bot.event
async def on_message(message):
    global streak_message, streak_count, streak_users, sequence_position

    # Ignore messages from the bot itself
    if message.author == sentinel_bot.user:
        return

    # Check if the message was sent in the desired channel
    desired_channel_id = 798371943324844042  # Replace with the ID of the desired channel
    if message.channel.id != desired_channel_id:
        return

    # Check for Captain Planet streak message sequence
    if sequence_position < len(constants.STREAK_MESSAGE_SEQUENCE) and message.content.lower() == constants.STREAK_MESSAGE_SEQUENCE[sequence_position]:
        print(f'{message.author} said {constants.STREAK_MESSAGE_SEQUENCE[sequence_position]}')
        sequence_position += 1
        streak_users.append(message.author)
        streak_count += 1
        if sequence_position == len(constants.STREAK_MESSAGE_SEQUENCE):
            print('Captain Planet Summoned')
            reset_streak()
            captain_planet_url = "https://media.tenor.com/WrD2KCj7EEIAAAAC/captain-planet.gif"
            image_data = get_image_data(captain_planet_url)
            caption = "By your powers combined... I AM CAPTAIN PLANET!"
            await message.channel.send(content=caption, file=discord.File(image_data, "captain_planet.gif"))

        return

    # If there is no current streak message, set the message and return
    if streak_message is None:
        streak_message = message.content
        streak_users = [(message.author, 1)]
        streak_count = 1
        return

    # If the message matches the streak message
    if message.content.lower() == streak_message.lower():

        # If the streak was broken, end the game
        if streak_count >= streak_threshold and message.author == streak_users[-1][0]:
            await message.channel.send(f'{message.author.mention} failed, can\'t pasta twice bruv, better luck next time!')
            reset_streak()
            print(f"Streak ended: {streak_message}, {streak_count}, {streak_users}")
            return

        # Add the user to the set of streak participants
        streak_users.append((message.author, streak_count))

        # Increment the streak count
        streak_count += 1

        # If the streak threshold has been reached, announce the start of the contest and add reactions
        if streak_count == streak_threshold:
            await message.channel.send(f'PASTA ALERT! **{streak_message}** has been pasta\'d {streak_threshold} times, how long can we keep it going?')
            await add_reactions(message)

        # If the streak count is above the threshold, add reactions for the current streak count
        elif streak_count > streak_threshold:
            await add_reactions(message, streak_count - streak_threshold)
    elif streak_count >= streak_threshold and sequence_position > 0:
        await message.channel.send(f'{message.author.mention} do you hate the planet or something? Be more considerate of our environment, ser.')
        reset_streak()
        streak_message = message.content
        streak_users = [(message.author, 1)]
        streak_count = 1
    # If the message does not match the streak message, reset the streak
    else:
        if streak_count >= streak_threshold:
            await message.channel.send(f'{message.author.mention} has broken the pasta, thx for nothing buzzkill. Better luck next time!')
        reset_streak()
        streak_message = message.content
        streak_users = [(message.author, 1)]
        streak_count = 1


###SENTINEL BOT END###

#run
loop = asyncio.get_event_loop()

loop.create_task(oib.bot.start(os.environ['INDEX_BOT_TOKEN']))

loop.create_task(gpb.bot.start(os.environ['GOHM_PRICE_BOT_TOKEN']))

loop.create_task(opb.bot.start(os.environ['OHM_BOT_TOKEN']))

loop.create_task(mcap_bot.start(os.environ['MCAP_BOT_TOKEN']))

loop.create_task(sentinel_bot.start(os.environ['SENTINEL_BOT_TOKEN']))

loop.create_task(olbb.bot.start(os.environ['LB_SMA_BOT_TOKEN']))

try:
  loop.run_forever()
finally:
  loop.stop()