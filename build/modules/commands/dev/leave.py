import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="leave", description="[DEV] Make OnlyOneMessage leave a guild")
    @app_commands.describe(guild_id="The ID of the guild to leave")
    async def leave(self, interaction: discord.Interaction, guild_id: str):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
        
        logmsg("DEBUG", "/leave executed", 
               function="leave", guild=str(interaction.guild.id))

        try:
            guild_id_int = int(guild_id)
            
        except ValueError:
            await interaction.response.send_message("Invalid guild ID: Must be a number", ephemeral=True)
            return

        guild = self.bot.get_guild(guild_id_int)
        if guild:
            try:
                await guild.leave()
                logmsg("DEBUG", f"Successfully left {guild.name} {guild.id}", function="leave")
                await interaction.response.send_message(f"Successfully left `{guild.name}` (`{guild.id}`)", ephemeral=True)
                
            except Exception as e:
                logmsg("DEBUG", f"Failed to leave guild {guild.name}: {e}", function="leave")
                await interaction.response.send_message(f"❌ Error while leaving guild:\n```\n{e}\n```", ephemeral=True)
                
        else:
            logmsg("DEBUG", "Guild not detected", function="leave")
            await interaction.response.send_message("Guild not found or bot is not in that guild.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Misc(bot))
