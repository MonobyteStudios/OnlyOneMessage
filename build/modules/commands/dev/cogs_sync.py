import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg

class LoadedReloadCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="loadedcogs", description="[DEV] Shows the currently loaded cogs")
    async def loaded_cogs(self, interaction: discord.Interaction):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        logmsg("DEBUG", f"/loadedcogs executed", 
               function="loadedcogs", guild=str(interaction.guild.id))

        loaded = "\n".join(self.bot.extensions.keys()) or "No cogs loaded."
        await interaction.response.send_message(f"**Loaded Cogs:**\n```\n{loaded}\n```", ephemeral=True)


    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="reloadcogs", description="[DEV] Reloads all cogs")
    async def reloadcogs(self, interaction: discord.Interaction):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        logmsg("DEBUG", "/reloadcogs executed", 
            guild=str(interaction.guild.id), function="reloadcogs")
        await interaction.response.defer(ephemeral=True)

        results, elapsed = await self.bot.load_all_extensions(self.bot)
        summary = (f"**Reload Cogs Complete**\n"
                f"- Elapsed: {elapsed:.1f}s\n"
                f"- Reloaded: {results['reloaded']}\n"
                f"- Failed: {results['failed']}\n"
                f"- Skipped: {results['skipped']}\n")

        await interaction.followup.send(summary, ephemeral=True)



async def setup(bot):
    await bot.add_cog(LoadedReloadCogs(bot))
