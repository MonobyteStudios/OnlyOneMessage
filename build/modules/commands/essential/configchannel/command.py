import discord
from discord.ext import commands
from discord import app_commands

from essential.logging import logmsg
from essential.checks import user_check
from essential.data import create_guild_data
from essential.autocomplete import set_channel_autocomplete

async def refreshview(guild: discord.Guild, bot, channel):
    from .views.__messageoptions__ import settingOptions
    from .views.__info__ import settingOptions as Info

    functions = [
        Info,
        settingOptions,
    ]

    view = discord.ui.LayoutView(timeout=None)

    for func in functions:
        items = await func(guild, bot, channel)

        container = discord.ui.Container()
        for item in items:
            container.add_item(item)

        view.add_item(container)

    logmsg("DEBUG", "Refreshed config view",
              guild=str(guild.id), function="refreshview")
    return view




class ConfigChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.database = self.bot.database
        self.serverdata = self.bot.serverdata


    @app_commands.command(name="configchannel", description="Configure a channel configured by OnlyOneMessage")
    @user_check(manage_roles=True, manage_channels=True)
    @app_commands.describe(
        channel="Select a channel to configure"
    )
    @app_commands.autocomplete(channel=set_channel_autocomplete)
    async def configchannel(self, interaction: discord.Interaction, channel: str):
        channel = interaction.guild.get_channel(int(channel))

        logmsg("DEBUG", "/configchannel command executed",
                guild=str(interaction.guild.id), function="configchannel")
        
        create_guild_data(self.bot, interaction.guild.id)
        view = await refreshview(interaction.guild, self.bot, channel)

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigChannel(bot))