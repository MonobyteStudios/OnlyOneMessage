import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg
import json
import io


class GuildData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverdata = self.bot.serverdata

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="guilddata", description="[DEV] Show the database JSON for a guild")
    @app_commands.describe(guild_id="The ID of the guild to inspect")
    async def guilddata(self, interaction: discord.Interaction, guild_id: str):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        logmsg("DEBUG", "/guilddata executed",
               function="guilddata", guild=str(interaction.guild.id))

        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.response.send_message("Invalid guild ID: Must be a number.", ephemeral=True)
            return

        data = self.serverdata.find_one({"_id": guild_id_int})
        if not data:
            await interaction.response.send_message("No data was found for the provided guild.", ephemeral=True)
            return
        

        formatted = json.dumps(data, indent=2, default=str)
        if len(formatted) > 1990: # send as a file if the formatted string is too long for a message
            file = discord.File(
                io.BytesIO(formatted.encode("utf-8")),
                filename=f"{guild_id_int}.json"
            )
            await interaction.response.send_message(
                file=file,
                ephemeral=True
            )

        else:
            await interaction.response.send_message(f"```json\n{formatted}\n```", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GuildData(bot))