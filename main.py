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
from datetime import datetime, timedelta
from helpers import get_circulating_supply, get_price_ohm, get_price_gohm, get_raw_index, get_7d_lb_sma, get_7d_floating_supply, get_7d_agg_token_values, get_7d_lb_sma_raw, human_format

###GOHM PRICE BOT START###
olyprice_bot = commands.Bot(command_prefix="olyprice!")

cg = CoinGeckoAPI()
LAST_PRICE = -1

### log in
@olyprice_bot.event
async def on_ready():
    print(f"Logged in as {olyprice_bot.user.name}")
    print("------")
    if update_gohm_price.is_running():
        print("Task Already Running on_ready")
    else:
      await update_gohm_price.start()  # DYNAMIC

@olyprice_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    for guild in olyprice_bot.guilds:
        await olyprice_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"gOHM price"))
    await ctx.send("Yes ser, on it boss.")

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.PRICE_UPDATE_INTERVAL)
async def update_gohm_price():
    try:   
        newName = await get_gohm_price()
        print(f"Updating nickname to: {newName}")
        ## dynamic updates
    
        for guild in olyprice_bot.guilds:
            await guild.me.edit(nick=newName)
            await olyprice_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"gOHM price"))
    except:
        for guild in olyprice_bot.guilds:
            await olyprice_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"gOHM price"))
        print("likely discord rate limit")
        traceback.print_exc()

async def get_gohm_price():
    global LAST_PRICE

    raw_data = cg.get_price(ids='governance-ohm', vs_currencies='usd, eth')
    market_data = json.dumps(raw_data)
    json_data = json.loads(market_data)
    
    usdPrice = get_price_gohm() #fetches from latest subgraph block
    ethPrice = json_data["governance-ohm"]["eth"] #fetches from CG, not available in subgraph
  
    if LAST_PRICE != -1 and (abs(((usdPrice - LAST_PRICE) / usdPrice) * 100) > 10):
        print(f"Caught Price Exception, reverting to last price", {usdPrice} | {LAST_PRICE})
        return "{} | Ξ{}".format(human_format(LAST_PRICE),"%.2f" % round(ethPrice, 2))
    else:
        #print("else")
        LAST_PRICE = usdPrice
        name_val = "{} | Ξ{}".format(human_format(usdPrice),"%.2f" % round(ethPrice, 2))
    
    return name_val
###GOHM PRICE BOT END###

###OHM PRICE BOT START###
ohmprice_bot = commands.Bot(command_prefix="ohmprice!")

cg = CoinGeckoAPI()
LAST_OHM_PRICE = -1

### log in
@ohmprice_bot.event
async def on_ready():
    print(f"Logged in as {ohmprice_bot.user.name}")
    print("------")
    if update_ohm_price.is_running():
        print("Task Already Running on_ready")
    else:
      await update_ohm_price.start()  # DYNAMIC

@ohmprice_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    for guild in ohmprice_bot.guilds:
        await ohmprice_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"OHM price"))
    await ctx.send("Yes ser, on it boss.")

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.PRICE_UPDATE_INTERVAL)
async def update_ohm_price():
    try:   
        newName = await get_ohm_price()
        print(f"Updating nickname to: {newName}")
        ## dynamic updates
    
        for guild in ohmprice_bot.guilds:
            await guild.me.edit(nick=newName)
            await ohmprice_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM price"))
    except:
        for guild in ohmprice_bot.guilds:
            await ohmprice_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM price"))
        print("likely discord rate limit")
        traceback.print_exc()

async def get_ohm_price():
    global LAST_OHM_PRICE
    raw_data = cg.get_price(ids='olympus', vs_currencies='usd, eth')
    market_data = json.dumps(raw_data)
    json_data = json.loads(market_data)
    #print(json_data)
    usdPrice = get_price_ohm()
    ethPrice = json_data["olympus"]["eth"]
  
    if LAST_OHM_PRICE != -1 and (abs(((usdPrice - LAST_OHM_PRICE) / usdPrice) * 100) > 10):
        print(f"Caught Price Exception, reverting to last price", {usdPrice} | {LAST_OHM_PRICE})
        return "{} | Ξ{}".format(human_format(LAST_OHM_PRICE),"%.3f" % round(ethPrice, 3))
    else:
        #print("else")
        LAST_OHM_PRICE = usdPrice
        name_val = "{} | Ξ{}".format(human_format(usdPrice),"%.3f" % round(ethPrice, 3))
    
    return name_val
###OHM PRICE BOT END###

###OHM INDEX BOT START###
index_bot = commands.Bot(command_prefix="olyindex!")

### index bot log in
@index_bot.event
async def on_ready():
    print(f"Logged in as {index_bot.user.name}")
    print("------")
    if update_index.is_running():
      print("Task Already Running on_ready")
    else:
      await update_index.start()  # DYNAMIC

@index_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    for guild in index_bot.guilds:
        await index_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"OHM Index"))
    await ctx.send("Yes ser, on it boss.")

@index_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def forceupdate(ctx):
    await ctx.send("Yes ser, on it boss.")
    newName = await get_ohm_index()
    for guild in index_bot.guilds:
        await guild.me.edit(nick=newName)
        await index_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"OHM Index"))
    await ctx.send("Happy to report it has been updated!")

@tasks.loop(minutes=constants.GENERIC_UPDATE_INTERVAL)
async def update_index():
    try:
        newName = await get_ohm_index()
        print(f"Updating index bot nickname to: {newName}")
        ## dynamic updates
        for guild in index_bot.guilds:
            await guild.me.edit(nick=newName)
            await index_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM Index"))
    except:
        for guild in index_bot.guilds:
            await index_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM Index"))

async def get_ohm_index():
    rawindex = get_raw_index()
    
    name_val = round(float(rawindex),4)
  
    return str(name_val)
###OHM INDEX BOT END###

###OHM LB SMA BOT START###
lb_sma_bot = commands.Bot(command_prefix="ohmliq!")

### OHM LB SMA bot log in
@lb_sma_bot.event
async def on_ready():
    print(f"Logged in as {lb_sma_bot.user.name}")
    print("------")
    if update_lb.is_running():
      print("Task Already Running on_ready")
    else:
      await update_lb.start()  # DYNAMIC

@lb_sma_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    try:
        for guild in lb_sma_bot.guilds:
            await lb_sma_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
        await ctx.send("Yes ser, on it boss.")
    except:
        traceback.print_exc()

@lb_sma_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def forceupdate(ctx):
    try:
        await ctx.send("Yes ser, on it boss.")
        newName = await get_ohm_lb()
        for guild in lb_sma_bot.guilds:
            await guild.me.edit(nick=newName)
            await lb_sma_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
        await ctx.send("Happy to report it has been updated!")
    except:
        traceback.print_exc()

@lb_sma_bot.command(pass_context=True)
async def getrawfloating(ctx):
    try:
        await ctx.send("Yes ser, on it boss.")
        data = get_7d_floating_supply()
        embed = discord.Embed(title="7 Day Floating Supply", color=discord.Color.blue())
        for k, v in data.items():
            embed.add_field(name=k, value="{:,}".format(v), inline=False)
        await ctx.send(embed=embed)
    except:
        traceback.print_exc()

@lb_sma_bot.command(pass_context=True)
async def ping(ctx):
    today = datetime.utcnow().date()
    date_7d_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    embed = discord.Embed(title="Pong", color=discord.Color.blue())
    embed.add_field(name="Today(UTC)", value=today, inline=False)
    embed.add_field(name="7D Ago(UTC)", value=date_7d_ago, inline=False)
    await ctx.send(embed=embed)

@lb_sma_bot.command(pass_context=True)
async def getrawtokens(ctx):
    try:
        await ctx.send("Yes ser, on it boss.")
        data = get_7d_agg_token_values()
        embed = discord.Embed(title="7 Day Token Values", color=discord.Color.blue())
        for k, v in data.items():
            embed.add_field(name=k, value=f"${v:,.2f}", inline=False)
        await ctx.send(embed=embed)
    except:
        traceback.print_exc()

@lb_sma_bot.command(pass_context=True)
async def getrunninglb(ctx):
    try:
        await ctx.send("Yes ser, on it boss.")
        data = get_7d_lb_sma_raw()
        embed = discord.Embed(title="7 Day Liquid Backing", color=discord.Color.blue())
        for k, v in data.items():
            embed.add_field(name=k, value=f"${v:,.2f}", inline=False)
        await ctx.send(embed=embed)
    except:
        traceback.print_exc()

@tasks.loop(minutes=constants.LB_UPDATE_INTERVAL)
async def update_lb():
    try:
        newName = await get_ohm_lb()
        print(f"Updating lb sma bot nickname to: {newName}")
        ## dynamic updates
        for guild in lb_sma_bot.guilds:
            await guild.me.edit(nick=newName)
            await lb_sma_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
    except:
        traceback.print_exc()
        for guild in lb_sma_bot.guilds:
            await lb_sma_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))

async def get_ohm_lb():
    try:
        lb_val = get_7d_lb_sma()
    
        return human_format(lb_val)
    except:
        traceback.print_exc()
###OHM LB SMA BOT END###

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
streak_users = set()

# Define a function to add the appropriate number of reaction emojis
async def add_reactions(message):
    global streak_count
    if streak_count == streak_threshold:
        await message.add_reaction(u"\u2705")  # Green checkmark emoji
    elif streak_count <= 9:
        await message.add_reaction(str(streak_count) + u"\u20e3")
    else:
        tens_digit = streak_count // 10
        ones_digit = streak_count % 10
        await message.add_reaction(str(tens_digit) + u"\u20e3")
        await message.add_reaction(str(ones_digit) + u"\u20e3")


# Define a function to reset the streak variables
def reset_streak():
    global streak_message, streak_count, streak_users
    streak_message = None
    streak_count = 0
    streak_users = set()

@sentinel_bot.event
async def on_message(message):
    global streak_message, streak_count, streak_users

    # Ignore messages from the bot itself
    if message.author == sentinel_bot.user:
        return

    # Check if the message was sent in the desired channel
    desired_channel_id = 798371943324844042  # Replace with the ID of the desired channel
    if message.channel.id != desired_channel_id:
        return

    # If there is no current streak message, set the message and return
    if streak_message is None:
        streak_message = message.content
        streak_users.add(message.author)
        streak_count = 1
        return

    # If the message matches the streak message
    if message.content.lower() == streak_message.lower():
        if message.author == streak_users.pop():
            reset_streak()
            return
        # If the streak was broken, end the game
        if streak_count >= streak_threshold and message.author == streak_users.pop():
            await message.channel.send(f'{message.author.mention} has broken the streak, better luck next time')
            reset_streak()
            return

        # Add the user to the set of streak participants
        streak_users.add(message.author)

        # Increment the streak count
        streak_count += 1

        # If the streak threshold has been reached, announce the start of the contest and add reactions
        if streak_count == streak_threshold:
            await message.channel.send(f'{streak_message} has been detected {streak_threshold} times, let\'s see who breaks the streak!')
        
        # Add reactions for all messages after the streak threshold is hit
        if streak_count >= streak_threshold:
            await add_reactions(message)

    # If the message does not match the streak message, reset the streak
    else:
        if streak_count >= streak_threshold:
            await message.channel.send(f'{streak_users.pop().mention} has broken the streak, better luck next time')
        reset_streak()
        streak_message = message.content
        streak_users.add(message.author)
        streak_count = 1


###SENTINEL BOT END###

#run
loop = asyncio.get_event_loop()

loop.create_task(index_bot.start(os.environ['INDEX_BOT_TOKEN']))

loop.create_task(olyprice_bot.start(os.environ['GOHM_PRICE_BOT_TOKEN']))

loop.create_task(ohmprice_bot.start(os.environ['OHM_BOT_TOKEN']))

loop.create_task(mcap_bot.start(os.environ['MCAP_BOT_TOKEN']))

loop.create_task(sentinel_bot.start(os.environ['SENTINEL_BOT_TOKEN']))

loop.create_task(lb_sma_bot.start(os.environ['LB_SMA_BOT_TOKEN']))

try:
  loop.run_forever()
finally:
  loop.stop()