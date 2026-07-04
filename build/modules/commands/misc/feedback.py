import discord
from discord.ext import commands
from discord import app_commands

from essential.metadata import feedbackchannel, metricsLogging
from essential.checks import guild_only
from essential.logging import logmsg

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.globaldata = self.bot.globaldata

    @app_commands.command(name="feedback", description="Send feedback to the developers of OnlyOneMessage")
    @guild_only()
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.channel_id))
    async def feedback(self, interaction: discord.Interaction):
        logmsg("DEBUG", "/feedback executed", guild=str(interaction.guild.id), function="feedback")
        blacklists = self.globaldata.find_one({"_id": "blacklists"}) or {}

        if not blacklists.get(str(interaction.user.id)):
            modal = FeedbackModal()
            await interaction.response.send_modal(modal)

        else:
            await interaction.response.send_message("You arent allowed to use this command. If this was a mistake, join our [support server](https://onlyonemessage.monobyte.studio/support).", ephemeral=True)
            logmsg("DEBUG", f"/feedback - user {interaction.user.id} is blacklisted", 
                   guild=str(interaction.guild.id), function="feedback")     




class FeedbackModal(discord.ui.Modal, title="Feedback"):
    info = discord.ui.TextDisplay(
        content="*This form will be submitted to the developers of OnlyOneMessage. Misuse of this system may result in a blacklist!*"
    )

    answer = discord.ui.TextInput(
        label='Send Feedback',
        style=discord.TextStyle.paragraph,
        required=True,

        placeholder='Put your feedback here. Remember to be respectful and constructive.',
        max_length=750
    )


    async def on_submit(self, interaction: discord.Interaction):
        channel = discord.utils.get(interaction.guild.channels, id=feedbackchannel)
        if not channel:
            logmsg("ERROR", f"Feedback channel with ID {feedbackchannel} was not found. Please check the configuration.", 
                   guild=str(interaction.guild.id), function="feedback")
            return

        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container()

        container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    f"### 📝 Feedback\n"
                    f"`{interaction.user.name}` (`{interaction.user.id}`) has submitted feedback.\n"
                    f"```{self.answer.value[:750]}```" # truncate to 750 chars
                    
                ), accessory=discord.ui.Thumbnail(media=(interaction.user.avatar.url if interaction.user.avatar else "https://cdn.monobyte.studio/onlyonemessageweb/logos/logoanimated.gif"))
            )
        )

        view.add_item(container)
        await channel.send(view=view)

        await interaction.response.send_message("Thanks! Your feedback has been submitted.", ephemeral=True)
        logmsg("DEBUG", "Feedback submitted and sent to feedback channel",
                guild=str(interaction.guild.id), function="on_submit")



async def setup(bot):
    if metricsLogging and feedbackchannel:
        await bot.add_cog(Feedback(bot))

    else:
        logmsg("WARNING", "The feedback cog was not registered due to set configuration. To change this, edit the bot's metadata.", 
               function="feedback")