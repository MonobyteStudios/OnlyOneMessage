import discord
from discord.ext import commands
from discord import app_commands

from essential.checks import user_check, bot_check
from essential.logging import logmsg
from essential.data import create_guild_data
from essential.autocomplete import set_channel_autocomplete



class RemoveChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @app_commands.command(name="removechannel", description="Remove a channel from OnlyOneMessage's management")
    @user_check(manage_roles=True, manage_channels=True)
    @bot_check(manage_roles=True, manage_channels=True)
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.channel_id))
    @app_commands.describe(
        channel="Select a channel to remove from OnlyOneMessage's management",
    )
    @app_commands.autocomplete(channel=set_channel_autocomplete)
    async def removechannel(self, interaction: discord.Interaction, channel: str):
        channel = interaction.guild.get_channel(int(channel))

        try:
            logmsg("DEBUG", "/removechannel executed", 
                guild=str(interaction.guild.id), function="removechannel")
            
            await interaction.response.defer(ephemeral=True)
            
            create_guild_data(self.bot, interaction.guild.id)
            serverdata = self.bot.serverdata.find_one({"_id": interaction.guild.id}) or {}
            channeldata = serverdata.get("channels", {}).get(str(channel.id), {})

            if not channeldata:
                logmsg("DEBUG", f"Channel {channel.id} is not currently managed. Raising error.", 
                    guild=str(interaction.guild.id), function="removechannel")
                
                await interaction.followup.send(
                    "This channel is not currently configured with OnlyOneMessage. Use the `/addchannel` command to add this channel to OnlyOneMessage's management.",
                    ephemeral=True
                )
                return



            # remove channel data
            self.bot.serverdata.update_one(
                {"_id": interaction.guild.id},
                {"$unset": {f"channels.{str(channel.id)}": ""}}
            )
            logmsg("DEBUG", f"Removed channel data for channel {channel.id}",
                guild=str(interaction.guild.id), function="removechannel")
            

            # remove the blacklist role
            blacklistrole = channeldata.get("blacklistrole", None)
            if blacklistrole:
                blacklistrole = interaction.guild.get_role(blacklistrole)

                if blacklistrole:
                    await blacklistrole.delete()
                    logmsg("DEBUG", f"Deleted blacklist role {blacklistrole.id} for channel {channel.id}", 
                        guild=str(interaction.guild.id), function="removechannel")
                    


            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    f"## <:check:1471690195576295619> Action Successful\n"
                    f"{channel.mention} has been removed from OnlyOneMessage's management. No cooldowns will be applied.\n"

                    "If you wish to re-add this channel, use the `/addchannel` command."
                )
            )

            view.add_item(container)
            await interaction.followup.send(view=view, ephemeral=True)

            logmsg("DEBUG", f"/removechannel completed successfully for channel ID {channel.id}", 
                guild=str(interaction.guild.id), function="removechannel")



        except Exception as e:
            logmsg("ERROR", f"An error has occurred in /removechannel: {e}", 
                guild=str(interaction.guild.id), function="removechannel")


            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    "## <:warning:1471672225257099439> An error occured\n"

                    "An unknown error occured while removing this channel from OnlyOneMessage's management.\n"
                    "This error has been automatically logged for debugging. No action is required.\n\n"
                    "<:rightarrow:1471673398164852930> If this issue persists, please create a ticket in our [support server](https://onlyonemessage.monobyte.studio/support)."
                )
            )

            view.add_item(container)
            await interaction.followup.send(view=view, ephemeral=True)



async def setup(bot):
    await bot.add_cog(RemoveChannel(bot))