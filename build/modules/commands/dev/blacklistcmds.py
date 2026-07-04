import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg

class BlacklistCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.globaldata = self.bot.globaldata

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="blacklistid", description="[DEV] Blacklist a user from /feedback command")
    async def blacklistid(self, interaction: discord.Interaction, user_id: str):
        logmsg("DEBUG", "/blacklistid executed", function="blacklistid")

        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        blacklists = self.globaldata.find_one({"_id": "blacklists"})
        if blacklists:
            self.globaldata.update_one(
                {"_id": "blacklists"},
                {"$set": {str(user_id): True}}
            )

            logmsg("DEBUG", f"User {user_id} successfully added to ID blacklist",
                   function="blacklistid")
            await interaction.response.send_message(f"Successfully added `{user_id}` to ID blacklist.", ephemeral=True)


    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="unblacklistid", description="[DEV] Unblacklist a user from /feedback command")
    async def unblacklistid(self, interaction: discord.Interaction, user_id: str):
        logmsg("DEBUG", "/unblacklistid executed", function="unblacklistid")

        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        blacklists = self.globaldata.find_one({"_id": "blacklists"})
        if blacklists:
            self.globaldata.update_one(
                {"_id": "blacklists"},
                {"$unset": {str(user_id): ""}}
            )

            logmsg("DEBUG", f"User {user_id} successfully removed from ID blacklist", 
                   function="unblacklistid")
            await interaction.response.send_message(f"Successfully removed `{user_id}` from ID blacklist.", ephemeral=True)




async def setup(bot):
    await bot.add_cog(BlacklistCMDS(bot))
