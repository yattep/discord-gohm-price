### imports
import os
import discord
from discord.ext import commands
from discord.ext import tasks
import json
from pycoingecko import CoinGeckoAPI
import traceback

cg = CoinGeckoAPI()

bot = commands.Bot(command_prefix="olyprice!")

UPDATE_INTERVAL = 5  # (in minutes)

LAST_PRICE = -1
LAST_MCAP = -1

admin_role = "Community Managers"

### log in
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("------")
    if update_name.is_running():
        print("Task Already Running on_ready")
    else:
      await update_name.start()  # DYNAMIC

@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def fixpresence(ctx):
    for guild in bot.guilds:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"gOHM price from cg"))
    await ctx.send("Yes ser, on it boss.")

@bot.command(pass_context=True)
@commands.has_role("Community Managers")
async def getStats(ctx):
    await ctx.message.reply("beep boop")
    return

# update nickname/precense on UPDATE_INTERVAL - # DYNAMIC
@tasks.loop(minutes=UPDATE_INTERVAL)
async def update_name():
    newName = await get_gohm_price()
    print(f"Updating nickname to: {newName}")
    ## dynamic updates
    try:
        for guild in bot.guilds:
            await guild.me.edit(nick=newName)
            await bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"gOHM price from cg"))
    except:
        print("likely discord rate limit")
        traceback.print_exc()

## HELPERS
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '${}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                               ['', 'K', 'M', 'B', 'T'][magnitude])

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

#run
bot.run(os.environ['BOT_TOKEN'])