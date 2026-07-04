import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg
import json

class GlobalData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.globaldata = self.bot.globaldata

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="globaldata", description="[DEV] Show global data for OnlyOneMessage")
    async def guilddata(self, interaction: discord.Interaction):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        logmsg("DEBUG", "/guilddata executed",
            function="guilddata", guild=str(interaction.guild.id))



        data = self.globaldata.find_one({"_id": "global"})
        if not data:
            await interaction.response.send_message("No global data has been found.", ephemeral=True)
            return


        formatted = json.dumps(data, indent=2, default=str)
        if len(formatted) > 1990:
            await interaction.response.send_message(
                f"```json\n{formatted[:1990]}\n```\n...", ephemeral=True
            )

        else:
            await interaction.response.send_message(f"```json\n{formatted}\n```", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GlobalData(bot))
