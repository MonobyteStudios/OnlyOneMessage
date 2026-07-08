import json
import os
import discord


def getvar(key, file):
    try:
        with open(os.path.join("data", "json", file), 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get(key, None)
    
    except (ValueError, FileNotFoundError, json.JSONDecodeError):
        return None

version = getvar("version", "metadata.json") or "[N/A]"
build = getvar("build", "metadata.json") or "[N/A]"
copyright = getvar("copyright", "metadata.json") or "[N/A]"

metricsLogging = getvar("metrics_support", "metadata.json") if getvar("metrics_support", "metadata.json") is not None else True
apiSupported = getvar("api_support", "metadata.json") if getvar("api_support", "metadata.json") is not None else True

guildjoinchannel = int(getvar("guildjoinchannel", "channels.json") or 0)
guildleavechannel = int(getvar("guildleavechannel", "channels.json") or 0)
feedbackchannel = int(getvar("feedbackchannel", "channels.json") or 0)

DEV_GUILDS = [discord.Object(id=guild_id) for guild_id in getvar("internalguilds", "metadata.json") or []]