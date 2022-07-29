### imports
import os
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
    newName = await get_ohm_index()
    print(f"Updating index bot nickname to: {newName}")
    ## dynamic updates
    for guild in index_bot.guilds:
        await guild.me.edit(nick=newName)
        await index_bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"OHM Index"))

async def get_ohm_index():
    raw_data = requests.post(constants.SUBGRAPH_URL, json = constants.REQUEST_OBJ)
    json_data = json.loads(raw_data.text)
    rawindex = json_data["data"]["protocolMetrics"][0]["currentIndex"]
    
    name_val = round(float(rawindex),4)
  
    return str(name_val)

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

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=constants.GENERIC_UPDATE_INTERVAL)
async def update_arbi():
    newName = await get_arbi_bal()
    print(f"Updating Arbi Balance nickname to: {newName}")
    ## dynamic updates
    for guild in arbi_bot.guilds:
        await guild.me.edit(nick=newName)
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


#run
loop = asyncio.get_event_loop()

loop.create_task(index_bot.start(os.environ['INDEX_BOT_TOKEN']))

loop.create_task(arbi_bot.start(os.environ['ARBI_BOT_TOKEN']))

loop.create_task(olyprice_bot.start(os.environ['GOHM_PRICE_BOT_TOKEN']))

try:
  loop.run_forever()
finally:
  loop.stop()