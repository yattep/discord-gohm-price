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
import requests
import asyncio
from helpers import human_format
from web3.auto.infura import w3
from web3 import Web3, HTTPProvider

###GOHM PRICE BOT START###
olyprice_bot = commands.Bot(command_prefix="olyprice!")

cg = CoinGeckoAPI()
LAST_PRICE = -1
LAST_MCAP = -1

### log in
@olyprice_bot.event
async def on_ready():
    print(f"Logged in as {olyprice_bot.user.name}")
    print("------")
    if update_price.is_running():
        print("Task Already Running on_ready")
    else:
      await update_price.start()  # DYNAMIC

@olyprice_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    for guild in olyprice_bot.guilds:
        await olyprice_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"gOHM price from cg"))
    await ctx.send("Yes ser, on it boss.")

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.PRICE_UPDATE_INTERVAL)
async def update_price():
    newName = await get_gohm_price()
    print(f"Updating nickname to: {newName}")
    ## dynamic updates
    try:
        for guild in olyprice_bot.guilds:
            await guild.me.edit(nick=newName)
            await olyprice_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"gOHM price from cg"))
    except:
        print("likely discord rate limit")
        traceback.print_exc()

async def get_gohm_price():
    global LAST_PRICE
    raw_data = cg.get_price(ids='governance-ohm', vs_currencies='usd, eth')
    market_data = json.dumps(raw_data)
    json_data = json.loads(market_data)
    #print(json_data)
    usdPrice = json_data["governance-ohm"]["usd"]
    ethPrice = json_data["governance-ohm"]["eth"]
  
    if LAST_PRICE != -1 and (abs(((usdPrice - LAST_PRICE) / usdPrice) * 100) > 10):
        print(f"Caught Price Exception, reverting to last price", {usdPrice} | {LAST_PRICE})
        return "{} | Ξ{}".format(human_format(LAST_PRICE),"%.2f" % round(ethPrice, 2))
    else:
        #print("else")
        LAST_PRICE = usdPrice
        name_val = "{} | Ξ{}".format(human_format(usdPrice),"%.2f" % round(ethPrice, 2))
    
    return name_val
###GOHM PRICE BOT END###

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
    raw_data = requests.post(constants.SUBGRAPH_URL, json = constants.REQUEST_OBJ)
    json_data = json.loads(raw_data.text)
    rawindex = json_data["data"]["protocolMetrics"][0]["currentIndex"]
    
    name_val = round(float(rawindex),4)
  
    return str(name_val)
###OHM INDEX BOT END###

###GOHM ARBI BAL BOT START###
arbi_bot = commands.Bot(command_prefix="arbibal!")
### arbi bot login
@arbi_bot.event
async def on_ready():
    print(f"Logged in as {arbi_bot.user.name}")
    print("------")
    if update_arbi.is_running():
        print("Task Already Running on_ready")
    else:
        await update_arbi.start()  # DYNAMIC

@arbi_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def fixpresence(ctx):
    for guild in arbi_bot.guilds:
        await arbi_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"Arbi gOHM Bal"))
    await ctx.send("Yes ser, on it boss.")

@arbi_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def forceupdate(ctx):
    await ctx.send("Yes ser, on it boss.")
    newName = await get_arbi_bal()
    for guild in arbi_bot.guilds:
        await guild.me.edit(nick=newName)
        await arbi_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"Arbi gOHM Bal"))
    await ctx.send("Happy to report it has been updated!")

@arbi_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def checkloop(ctx):
    try:
      if update_arbi.is_running():
        next_iter = update_arbi.next_iteration
        next_run = next_iter.strftime(constants.DATE_FORMAT)
        await ctx.send(f"Loop is Running, next loop attempt at: {next_run}")
      else:
        await ctx.send("Loop is not Running")
    except Exception as e:
      await ctx.send(f"Exception Raised, check logs: {e}")

@arbi_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)
async def startloop(ctx):
    try:
      if update_arbi.is_running():  
        await ctx.send("Loop Already Running")
      else:
        update_arbi.start()
        await ctx.send("Started Loop")
    except Exception as e:
      await ctx.send(f"Exception Raised, check logs: {e}")


# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.GENERIC_UPDATE_INTERVAL)
async def update_arbi():
    try:
        newName = await get_arbi_bal()
        print(f"Updating Arbi Balance nickname to: {newName}")
        ## dynamic updates
        for guild in arbi_bot.guilds:
            await guild.me.edit(nick=newName)
            await arbi_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"Arbi gOHM Bal"))
    except:
        print(f"Failed to update Arbi Balance nickname")
        for guild in arbi_bot.guilds:
            await arbi_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"Arbi gOHM Bal"))

async def get_arbi_bal():
    gohm_abi = json.loads(constants.GOHM_ABI)
    
    connection = Web3(HTTPProvider('https://arbitrum-mainnet.infura.io/v3/86ca5cc7ad4e4d528a574bffa611c22e'))
    
    token = connection.eth.contract(w3.toChecksumAddress(constants.GOHM_TOKEN_ADDR),abi=gohm_abi)
    
    balance = token.functions.balanceOf(w3.toChecksumAddress(constants.CONTRACT_ADDR)).call()
    
    balanceasgwei = w3.fromWei(balance,"ether")
    balancerounded = round(balanceasgwei,4)
    
    return str(balancerounded)
###GOHM ARBI BAL BOT END###

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

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.GENERIC_UPDATE_INTERVAL)
async def update_mcap():
    newName = await get_ohm_mcap()
    print(f"Updating nickname to: {newName}")
    ## dynamic updates
    try:
        for guild in mcap_bot.guilds:
            await guild.me.edit(nick=newName)
            await mcap_bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM MCAP"))
    except:
        print("likely discord rate limit")

async def get_ohm_mcap():
    global LAST_VAL
    try:
      raw_data = requests.post(constants.SUBGRAPH_URL, json = constants.REQUEST_OBJ)
      json_data = json.loads(raw_data.text)
      mcap = json_data["data"]["protocolMetrics"][0]["marketCap"]
      name_val = human_format(float(mcap))
      LAST_VAL = name_val
      return name_val
    except:
      print("subgraph exception")
      return LAST_VAL
###OHM MCAP BOT END###

###SENTINEL BOT START###
### intents (double check dev portal)
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
        print(f"Couldn't locate member {member.id} | {member.name}")
    if member_check is not None:
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

###SENTINEL BOT END###

#run
loop = asyncio.get_event_loop()

loop.create_task(index_bot.start(os.environ['INDEX_BOT_TOKEN']))

loop.create_task(arbi_bot.start(os.environ['ARBI_BOT_TOKEN']))

loop.create_task(olyprice_bot.start(os.environ['GOHM_PRICE_BOT_TOKEN']))

loop.create_task(mcap_bot.start(os.environ['MCAP_BOT_TOKEN']))

loop.create_task(sentinel_bot.start(os.environ['SENTINEL_BOT_TOKEN']))

try:
  loop.run_forever()
finally:
  loop.stop()