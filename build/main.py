# imports
import discord
import time
import traceback
import pathlib
from discord.ext import commands
from dotenv import load_dotenv
import os
from collections import Counter
from essential.metadata import version, devBranch, build, copyright, DEV_GUILDS
from essential.logging import logmsg


with open(os.path.join("data", "log.log"), 'a') as f:
    f.write("\n -- APP STARTUP REQUESTED -- \n")

logmsg("INFO", "Startup request received - OnlyOneMessage is booting...", function="startup")
logmsg("INFO", f"OnlyOneMessage {version} [Build {build}]", function="startup")
logmsg("INFO", copyright, function="startup")

if devBranch:
    logmsg("NOTICE", "OnlyOneMessage is running on the ***development*** token. If this was unintentional, terminate the process and set 'development' in metadata to False.", 
           function="startup")
else:
    logmsg("NOTICE", "OnlyOneMessage is running on the PRODUCTION token. If this was unintentional, terminate the process and set 'development' in metadata to True.", 
           function="startup")
    


intents = discord.Intents.all()
intents.presences = False
intents.message_content = False

client = commands.AutoShardedBot(
    command_prefix=">", 
    help_command=None, 
    intents=intents
)



async def load_all_extensions(bot):
    bot.load_all_extensions = load_all_extensions # allow other modules to call this function

    load_start = time.perf_counter()
    results = Counter()
    
    base_path = pathlib.Path(os.path.join("build", "modules"))
    logmsg("DEBUG", f"Loading modules from {base_path}...", 
           function="load_all_extensions")

    try:
        module_name = "modules.core.mongodb"
        if module_name in bot.extensions:
            await bot.unload_extension(module_name)
            results["reloaded"] += 1

        await bot.load_extension(module_name)
        logmsg("DEBUG", f"{module_name} has been loaded successfully!", 
               function="load_all_extensions")
        
        results["loaded"] += 1

    except Exception as e:
        error_traceback = traceback.format_exc()
        logmsg("ERROR", f"Failed to load {module_name}:\n{error_traceback}", 
               function="load_all_extensions")
        
        results["failed"] += 1
        raise e

    # ---


    exclude = {"mongodb.py"} # modules to skip
    for file in base_path.rglob("*.py"):
        if (
            any(part in exclude for part in file.parts) or 
            file.name.startswith("_") # skip modules starting with _
        ):
            results["skipped"] += 1
            continue

        relative_path = file.relative_to(base_path.parent)
        module_path = ".".join(relative_path.with_suffix('').parts)

        try:
            with open(file, encoding="utf-8") as f:
                if module_path in bot.extensions:
                    await bot.unload_extension(module_path)
                    results["reloaded"] += 1

                await bot.load_extension(module_path)
                logmsg("DEBUG", f"{module_path} has been loaded successfully!", 
                        function="load_all_extensions")
                
                results["loaded"] += 1

        except Exception:
            error_traceback = traceback.format_exc()
            logmsg("ERROR", f"Failed to load {module_path}:\n{error_traceback}", 
                   function="load_all_extensions")
            
            results["failed"] += 1


    load_end = time.perf_counter()
    elapsed = round(load_end - load_start, 1)

    logmsg("INFO", f"Module loading completed in {elapsed}s!", function="load_all_extensions")
    logmsg("INFO", (
        f"Loaded {results['loaded']} module(s), reloaded {results.get('reloaded', 0)} module(s), "
        f"skipped {results['skipped']} module(s), failed to load {results['failed']} module(s)!"
    ), function="load_all_extensions")

    return results, elapsed




@client.event
async def on_ready():
    logmsg("INFO", "Loading modules...", function="startup")
    await load_all_extensions(client)

    client.StartTime = time.time() # sets starttime to current time
    logmsg("INFO", f"Syncing slash commands...", function="startup")

    try:
        synced = await client.tree.sync()
        logmsg("INFO", f"Successfully synced {len(synced)} normal command(s)!", function="startup")


        synceddev = [] # sync development commands
        for guild in DEV_GUILDS:
            cmds = await client.tree.sync(guild=guild)
            synceddev.extend(cmds)

        logmsg("INFO", f"Successfully synced {len(synceddev) - len(synced)} internal command(s)!", function="startup")


    except Exception as e:
        content2 = f"An error has occured while attempting to sync slash commands: **{e}**"
        logmsg("ERROR", content2, function="startup")


    logmsg("INFO", f"OnlyOneMessage has successfully started on {version}!", 
           function="startup")




load_dotenv(dotenv_path=os.path.join("data", ".env")) # load bot token
PROD_TOKEN = os.getenv('PROD_TOKEN')
DEV_TOKEN = os.getenv('DEV_TOKEN')

if not devBranch:
    BOT_TOKEN = PROD_TOKEN

else:
    BOT_TOKEN = DEV_TOKEN

client.run(BOT_TOKEN)