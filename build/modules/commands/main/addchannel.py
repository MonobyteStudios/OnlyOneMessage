import discord
from discord.ext import commands
from discord import app_commands

from essential.checks import user_check, bot_check
from essential.logging import logmsg, event
from essential.data import create_guild_data

def format_duration(seconds):
    try:
        seconds = int(seconds)

    except ValueError:
        raise ValueError(f"Invalid duration value: {seconds}")

    if seconds == 0:
        return "Forever"

    units = [
        ('day', 86400),
        ('hour', 3600),
    ]

    for name, duration in units:
        if seconds % duration == 0:
            count = seconds // duration
            return f"{count} {name}" + ("s" if count != 1 else "")

    return f"{seconds} seconds"



class AddChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addchannel", description="Add a channel for OnlyOneMessage to manage cooldowns")
    @user_check(manage_roles=True, manage_channels=True, manage_threads=True)
    @bot_check(manage_roles=True, manage_threads=True, manage_channels=True)
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.channel_id))
    @app_commands.describe(
        channel="Select a channel",
        duration="Select the cooldown duration"
    )
    @app_commands.choices(
        duration=[
            app_commands.Choice(name="12 Hours", value=43200),
            app_commands.Choice(name="1 Day", value=86400),
            app_commands.Choice(name="3 Days", value=259200),
            app_commands.Choice(name="7 Days", value=604800),
            app_commands.Choice(name="14 Days", value=1209600),
            app_commands.Choice(name="1 Month", value=2592000),
            app_commands.Choice(name="Forever", value=0),
        ]
    )
    async def addchannel(self, interaction: discord.Interaction, channel: discord.TextChannel, duration: app_commands.Choice[int]):
        try:
            logmsg("DEBUG", "/addchannel executed", 
                guild=str(interaction.guild.id), function="addchannel")
            
            await interaction.response.defer(ephemeral=True)
            
            create_guild_data(self.bot, interaction.guild.id)
            serverdata = self.bot.serverdata.find_one({"_id": interaction.guild.id}) or {}
            channeldata = serverdata.get("channels", {}).get(str(channel.id), {})



            # check if OnlyOneMessage can manage this channel
            perms = channel.permissions_for(interaction.guild.me)
            missing_perms = [] # list of missing permissions

            if not perms.view_channel:
                missing_perms.append("View Channel")
            if not perms.send_messages:
                missing_perms.append("Send Messages")
            if not perms.manage_channels:
                missing_perms.append("Manage Channel")
            if not perms.manage_permissions:
                missing_perms.append("Manage Permissions")
                
            if missing_perms:
                event("SetupFailedPermissions")
                logmsg("DEBUG", f"Missing permissions for channel {channel.id}: {', '.join(missing_perms)}. Raising error.", 
                    guild=str(interaction.guild.id), function="addchannel")
                
                view = discord.ui.LayoutView(timeout=None)
                container = discord.ui.Container()

                container.add_item(
                    discord.ui.TextDisplay(
                        "## <:warning:1471672225257099439> I can't manage this channel!\n"

                        f"I dont have the following permissions in the channel {channel.mention}: "
                        f"{', '.join(f'`{perm}`' for perm in missing_perms)}\n\n"

                        "<:rightarrow:1471673398164852930> Please ensure I have these permissions, then try running `/addchannel` again."
                    )
                )
                view.add_item(container)

                await interaction.followup.send(view=view, ephemeral=True)
                return
            

            


            blacklistrole = discord.utils.get(interaction.guild.roles, id=channeldata.get("blacklist_role", 0))
            if not blacklistrole: # create if it doesn't exist
                blacklistrole = await interaction.guild.create_role(
                    name=f"oom-{channel.name}",
                    reason=f"OnlyOneMessage channel setup (Executed by {interaction.user.name})",
                    mentionable=False,
                )
                logmsg("DEBUG", f"Successfully created blacklist role {blacklistrole.id} for channel ID {channel.id}", 
                        guild=str(interaction.guild.id), function="addchannel")
                
            else:
                logmsg("DEBUG", f"Blacklist role {blacklistrole.id} already exists for channel ID {channel.id}", 
                        guild=str(interaction.guild.id), function="addchannel")



            # assign permissons for the blacklist role in the channel
            await channel.edit(slowmode_delay=0, reason=f"OnlyOneMessage channel setup (Executed by {interaction.user.name})")
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            overwrite.create_private_threads = False
            overwrite.create_public_threads = False
            overwrite.send_messages_in_threads = False

            try: # common failure point here, so we try except this specific point
                await channel.set_permissions(
                    blacklistrole,
                    overwrite=overwrite,
                    reason=f"OnlyOneMessage channel setup (Executed by {interaction.user.name})"
                )
                logmsg("DEBUG", "Successfully set role permissions for blacklist role", 
                        guild=str(interaction.guild.id), function="addchannel")
                

            except discord.Forbidden:
                event("SetupFailedPermissions")
                logmsg("WARNING", "Failed to set role permissions: Forbidden", 
                    guild=str(interaction.guild.id), function="addchannel")

                view = discord.ui.LayoutView(timeout=None)
                container = discord.ui.Container()

                container.add_item(
                    discord.ui.TextDisplay(
                        "## <:warning:1471672225257099439> I don't have permission!\n"

                        f"I don't have permission to edit role permissions for the {channel.mention} channel. "
                        "Please ensure I have the proper permissions and try again.\n\n"
                        "<:rightarrow:1471673398164852930> If this issue persists, please create a ticket in our [support server](https://onlyonemessage.monobyte.studio/support)."
                    )
                )

                view.add_item(container)

                await interaction.followup.send(view=view, ephemeral=True)
                return
            



            # create channel data & insert into database
            channeldata = {
                "blacklist_role": blacklistrole.id,
                "recovery": False,
                "reactions": False,
                "cooldown": duration.value,
                "cooldown_cache": {},
            }
            self.bot.serverdata.update_one(
                {"_id": interaction.guild.id},
                {"$set": {f"channels.{channel.id}": channeldata}},
                upsert=True
            )
            logmsg("DEBUG", f"Channel data for ID {channel.id} created",
                    guild=str(interaction.guild.id), function="addchannel")



            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    f"## <:check:1471690195576295619> Action Successful\n"
                    f"{channel.mention}'s cooldown has been set to `{format_duration(duration.value)}`.\n"

                    "If you wish to update this channel's configuration, use the `/configchannel` command."
                )
            )

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    f"-# A role has been made, {blacklistrole.mention}, to manage cooldowns for this channel. Make sure you keep it in a safe place!"
                )
            )
            

            view.add_item(container)
            await interaction.followup.send(view=view, ephemeral=True)
            await send_channel_message(interaction, self.bot, channel)

            logmsg("DEBUG", f"/addchannel completed successfully for channel ID {channel.id}", 
                guild=str(interaction.guild.id), function="addchannel")



        except Exception as e:
            event("SetupFailedUnknown")
            logmsg("ERROR", f"An error has occurred in /addchannel: {e}", 
                guild=str(interaction.guild.id), function="addchannel")


            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    "## <:warning:1471672225257099439> An error occured\n"

                    "An unknown error occured while setting this channel's slowmode.\n"
                    "This error has been automatically logged for debugging. No action is required.\n\n"
                    "<:rightarrow:1471673398164852930> If this issue persists, please create a ticket in our [support server](https://onlyonemessage.monobyte.studio/support)."
                )
            )

            view.add_item(container)
            await interaction.followup.send(view=view, ephemeral=True)
            
            import sentry_sdk
            sentry_sdk.capture_exception(e)




async def send_channel_message(interaction: discord.Interaction, bot, channel):
    if channel: # make sure channel exists before trying to send message
        serverdata = bot.serverdata.find_one({"_id": interaction.guild.id}) or {}
        channeldata = serverdata.get("channels", {}).get(str(channel.id), {})

        try:
            await channel.send(
                f"-# This channel's cooldown has been set to `{format_duration(channeldata.get('cooldown', 0))}`."
            )

        except discord.Forbidden:
            logmsg("WARNING", f"Failed to send message in channel {channel.id}: Forbidden", 
                guild=str(interaction.guild.id), function="send_channel_message")




async def setup(bot):
    await bot.add_cog(AddChannel(bot))