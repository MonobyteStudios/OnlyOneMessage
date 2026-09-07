import discord
from discord.ext import commands
from discord import app_commands
from essential.logging import logmsg


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.error(self.errorhandler)


    async def send_error_message(self, interaction: discord.Interaction, title: str, description: str):
        try:
            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    f"## {title}\n"
                    f"{description}"
                )
            )
            view.add_item(container)
    
            await interaction.response.send_message(view=view, ephemeral=True)

        except discord.InteractionResponded:
            await interaction.followup.send(view=view, ephemeral=True)

        logmsg("DEBUG", f"Error message sent successfully!", function="send_error_message")




    async def errorhandler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        logmsg("DEBUG", "Error handler executed for app commands", 
               function="errorhandler")


        if isinstance(error, app_commands.CommandOnCooldown):
            logmsg("DEBUG", "Error: CommandOnCooldown detected", function="errorhandler")
            await self.send_error_message(
                interaction,
                "<:warning:1471672225257099439> This command is on cooldown!",
                f"Please wait {error.retry_after:.1f} second(s) before executing this command again."
            )


        elif isinstance(error, app_commands.BotMissingPermissions):
            logmsg("DEBUG", "BotMissingPermissions error detected", 
                   function="errorhandler")
            
            await self.send_error_message(
                interaction,
                "<:warning:1471672225257099439> I don't have permission!",
                
                f"OnlyOneMessage does not have permission to execute this command. "
                f"Please refer to this error message to add required permissions:\n\n`{error}`"
            )


        elif isinstance(error, app_commands.MissingPermissions):
            logmsg("DEBUG", "MissingPermissions error detected", function="errorhandler")
            await self.send_error_message(
                interaction,
                "<:warning:1471672225257099439> Missing Permissions",
                f"{error} Please try again when you get the required permission(s)."
            )


        elif isinstance(error, app_commands.NoPrivateMessage):
            logmsg("DEBUG", "NoPrivateMessage error detected", function="errorhandler")
            await self.send_error_message(
                interaction,
                "<:warning:1471672225257099439> Commands are not available in DMs",
                "This command cannot be used in DMs. Please use it in a server."
            )


        else:
            import traceback
            logmsg("ERROR", f"An unknown error has been detected:\n {traceback.format_exc()}", 
                   function="errorhandler")

            await self.send_error_message(
                interaction,
                "<:warning:1471672225257099439> Unknown Error",
                "An unknown error has occurred internally. This error has been logged successfully "
                "and our developer team will investigate into it. If this issue persists, please create a ticket in our support server."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))
