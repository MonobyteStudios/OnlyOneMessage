import discord
from discord.ext import commands
from discord import app_commands

from .__configutils__ import logconfig as _logconfig
from essential.logging import logmsg
from essential.checks import user_check
from essential.data import create_guild_data

class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.database = self.bot.database
        self.serverdata = self.bot.serverdata
        
        self.bot.logconfig = _logconfig


    @app_commands.command(name="config", description="Configure global OnlyOneMessage settings for this server")
    @user_check(manage_roles=True, manage_channels=True)
    async def config(self, interaction: discord.Interaction):
        logmsg("DEBUG", "/config command executed",
                guild=str(interaction.guild.id), function="config")
        
        create_guild_data(self.bot, interaction.guild.id)

        from .__configutils__ import refreshview
        view = await refreshview(interaction.guild, self.bot)

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))