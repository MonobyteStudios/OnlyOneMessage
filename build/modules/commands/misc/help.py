import discord
from discord.ext import commands
from discord import app_commands
from essential.logging import logmsg

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class HelpView(discord.ui.LayoutView):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    "# ❓ Help\n"
                    "*View all available commands & support for OnlyOneMessage.*"
                ))

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    "### ⚙️ Main Commands\n"
                    f"`/addchannel` - Add a channel to manage cooldowns\n"
                    f"`/removechannel` - Remove a channel from management"
                ))
            
            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    "### 🛠️ Essential Commands\n"
                    f"`/config` - Configure global settings for OnlyOneMessage\n"
                    f"`/configchannel` - Configure a specific channel's settings\n"
                ))
            
            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    "### ❓ Misc. Commands\n"
                    f"`/invite` - Invite OnlyOneMessage to your server\n"
                    f"`/feedback` - Send feedback to the developers of OnlyOneMessage\n"
                    f"`/stats` - View global & server statistics for OnlyOneMessage"
                ))
            
            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    "### ⚡ Get Started\n"
                    f"1. Run `/addchannel` with the channel you want to use, plus its cooldown\n"
                    "2. Use `/configchannel` to configure the channel added\n"
                    f"3. Use `/config` to configure global settings\n"
                    "4. You're all set! 🎉"
                ))
            

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    f"OnlyOneMessage is maintained by Monobyte Studios ([monobyte.studio](https://monobyte.studio))\n"
                    f"Need help? Join our [support server](https://onlyonemessage.monobyte.studio/support)!"
                ))
            
            container.add_item(
                discord.ui.ActionRow(
                    discord.ui.Button(label="Terms of Service", url="https://onlyonemessage.monobyte.studio/terms", emoji="<:settings:1368591899111329854>"),
                    discord.ui.Button(label="Privacy Policy", url="https://onlyonemessage.monobyte.studio/privacy", emoji="<:lock:1368590733602459669>"),
                    discord.ui.Button(label="Source Code", url="https://github.com/MonobyteStudios/OnlyOneMessage"),
                )
            )


            self.add_item(container)
            
            

    @app_commands.command(name="help", description="View all available commands")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.channel_id))
    async def help(self, interaction: discord.Interaction):
        logmsg("DEBUG", '/help executed',
               function="help", guild=str(interaction.guild.id))

        view = self.HelpView(self.bot)
        await interaction.response.send_message(view=view)

        
async def setup(bot):
    await bot.add_cog(Help(bot))