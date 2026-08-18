import json
import os
import discord

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join("data", ".env"))

def getvar(key, file):
    try:
        with open(os.path.join("data", "json", file), 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get(key, None)
    
    except (ValueError, FileNotFoundError, json.JSONDecodeError):
        return None


VERSION = getvar("version", "metadata.json") or "[N/A]"
BUILD = getvar("build", "metadata.json") or "[N/A]"
COPYRIGHT = getvar("copyright", "metadata.json") or "[N/A]"

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
INTERNAL_GUILD_IDS = [int(x) for x in os.getenv("INTERNAL_GUILD_IDS", "").split(",") if x]
DEV_GUILDS = [discord.Object(id=guild_id) for guild_id in INTERNAL_GUILD_IDS]

API_SUPPORT = os.getenv("API_SUPPORT", False) # if not provided, default to False

GUILD_JOIN_CHANNEL = os.getenv("GUILD_JOIN_CHANNEL", None)
GUILD_LEAVE_CHANNEL = os.getenv("GUILD_LEAVE_CHANNEL", None)
FEEDBACK_CHANNEL = os.getenv("FEEDBACK_CHANNEL", None)