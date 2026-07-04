import discord
from essential.logging import logmsg
from essential.data import decrypt
import time
import aiohttp


async def refreshview(guild: discord.Guild, bot):
    from .views.__logging__ import settingOptions as LoggingOptions
    from .views.__botconfig__ import settingOptions as BotConfigOptions

    functions = [
        LoggingOptions,
        BotConfigOptions
    ]

    view = discord.ui.LayoutView(timeout=None)

    for func in functions:
        items = await func(guild, bot)

        container = discord.ui.Container()
        for item in items:
            container.add_item(item)

        view.add_item(container)

    logmsg("DEBUG", "Refreshed config view",
              guild=str(guild.id), function="refreshview")
    return view




cooldowns = {}
def parse_cooldown(id, cd_seconds=2): # cooldown parser to prevent spamming of config logs
    now = time.time()
    
    if id in cooldowns:
        if now < cooldowns[id]:
            return False
        
        else:
            del cooldowns[id]

    cooldowns[id] = now + cd_seconds
    return True


async def logconfig(bot, user: discord.User, valuename: str, value: str): # sends log for config changes
    cooldown = parse_cooldown(user.id)
    if not cooldown:
        return

    guild = user.guild if hasattr(user, 'guild') else None # get guild from user if possible (for DM interactions, user won't have guild attribute)
    if guild is None:
        return
    
    serverdata = bot.serverdata
    server_data = serverdata.find_one({"_id": guild.id})
    if server_data is None:
        return
    

    if server_data.get("config", {}).get("loggingchannelid") == 0:
        logmsg("DEBUG", "Logging disabled, skipping logconfig", 
               guild=str(guild.id), function="logconfig")
        return
    
    
    loggingcategories = server_data.get("config", {}).get("loggingcategories")
    if loggingcategories:
        if "config" not in loggingcategories:
            logmsg("DEBUG", "Config logging category disabled, skipping logconfig", 
                   guild=str(guild.id), function="logconfig")
            return
        


    embed = discord.Embed(
        title="⚙️ Configuration Update",
        description="A configuration update has been made to this server.",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(
        name="Details",
        value=(
            f"> **🎭 Author: {user.mention}**\n"
            f"> 🛠️ Setting: {valuename}\n"
            f"> 📜 Set to: {value}\n"
        ),
    )
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)


    # send the embed
    webhookurl = decrypt(server_data.get("config", {}).get("loggingchannel"))
    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhookurl, session=session)
            await webhook.send(embed=embed)

        logmsg("DEBUG", "Successfully sent config log",
            guild=str(guild.id), function="logconfig")
        

    except discord.NotFound:
        logmsg("WARNING", "Failed to send config log [Webhook not found]",
            guild=str(guild.id), function="logconfig")
        
    except discord.Forbidden:
        logmsg("WARNING", "Failed to send config log [Forbidden]",
            guild=str(guild.id), function="logconfig")
