import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg
import json
import io


class GlobalData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.globaldata = self.bot.globaldata

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="globaldata", description="[DEV] Show global data for OnlyOneMessage")
    async def globaldata(self, interaction: discord.Interaction):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        logmsg("DEBUG", "/globaldata executed",
               function="globaldata", guild=str(interaction.guild.id))


        cursor = self.globaldata.find({}) # find all documents in the globaldata collection
        docs = list(cursor)
        if not docs:
            await interaction.response.send_message("No global data was found.", ephemeral=True)
            return
        

        formatted = json.dumps(docs, indent=2, default=str)
        if len(formatted) > 1990: # send as a file if the formatted string is too long for a message
            file = discord.File(
                io.BytesIO(formatted.encode("utf-8")),
                filename="globaldata.json"
            )

            await interaction.response.send_message(
                file=file,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"```json\n{formatted}\n```", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GlobalData(bot))