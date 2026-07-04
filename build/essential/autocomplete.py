import discord
from discord.ext import commands
from discord import app_commands

from essential.logging import logmsg



async def set_channel_autocomplete(interaction: discord.Interaction, current: str):
    try: # get the guild from the interaction; if it fails return nothing
        guild = interaction.guild
        if guild is None:
            return []
        
    except Exception:
        return []
    guild_id = guild.id


    doc = interaction.client.serverdata.find_one({"_id": guild_id}) or {}
    channels = doc.get("channels", {})

    choices = []

    for channel_id in channels.keys():
        channel = guild.get_channel(int(channel_id))
        if channel and current.lower() in channel.name.lower():
            choices.append(
                app_commands.Choice(
                    name=f"#{channel.name}",
                    value=str(channel.id)
                )
            )

    logmsg("DEBUG", f"Autocomplete for channel selection returned {len(choices)} choices for input '{current}'", 
           function="set_channel_autocomplete", guild=int(guild_id))
    return choices[:25]