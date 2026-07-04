import discord
from discord.ext import commands
from essential.metadata import guildjoinchannel, guildleavechannel, metricsLogging
from essential.logging import logmsg, event
from essential.checks import is_guild_flooding
from essential.data import remove_guild_data

class GuildJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logmsg("DEBUG", "on_guild_join triggered", 
               guild=str(guild.id), function="on_guild_join")

        if is_guild_flooding(guild.id):
            logmsg("WARNING", f"Guild {guild.name} ({guild.id}) exceeded event rate limit.", 
                   guild=str(guild.id), function="on_guild_join")
            return


        try:
            for channel in guild.text_channels:
                channel = self.bot.get_channel(channel.id)
                perms = channel.permissions_for(guild.me)

                # checks for the channel
                if channel is None:
                    continue

                if not perms.send_messages or not perms.embed_links:
                    continue
                


                view = discord.ui.LayoutView(timeout=None)
                container = discord.ui.Container()

                container.add_item(
                    discord.ui.TextDisplay(
                        "## 👋 Welcome to OnlyOneMessage!\n"
                        "Hey there! OnlyOneMessage allows server admins **complete control** over text channel behavior. "
                        "Set slowmodes **beyond it's limit**, log **individual cooldowns**, and **fine-tune** settings for **each individual channel**, "
                        "all through a straightforward interface using Discord's slash commands."
                    )
                )

                container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

                container.add_item(
                    discord.ui.TextDisplay(
                        "### ❓ How does this bot work?\n"
                        "OnlyOneMessage will actively monitor a configured channel for new messages. "
                        "Once someone sends a message, they'll be given a custom role, "
                        "preventing them from sending additional messages or interacting with threads within that channel. "
                        "Once their cooldown expires, the custom role will **automatically be removed**, allowing them to chat again."
                    )
                )

                container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

                container.add_item(
                    discord.ui.TextDisplay(
                        "### ⚡ Get Started with OnlyOneMessage\n"
                        f"1. Run `/addchannel` with the channel you want to use, plus its cooldown`\n"
                        "2. Use `/configchannel` to configure the channel added\n"
                        f"3. Use `/config` to configure global settings\n"
                        "4. You're all set! 🎉"
                    )
                )

                container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

                container.add_item(
                    discord.ui.TextDisplay(
                        "### 💖 Thank You!\n"
                        "Thank you for choosing OnlyOneMessage! This bot was made with passion and we hope it serves you well."
                    )
                )

                
                container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))
                container.add_item(
                    discord.ui.TextDisplay(
                        "-# Get support or view available commands with `/help`"
                    )
                )


                view.add_item(container)

                await channel.send(view=view)
                logmsg("DEBUG", "Welcome message sent successfully", 
                        guild=str(guild.id), function="on_guild_join")
                break 



            # create embed for internal server
            if not metricsLogging:
                logmsg("WARNING", "Metrics collection is disabled due to set configuration. To change this, edit the bot's metadata.", 
                       function="on_guild_join")
                return
            
            guild_owner = self.bot.get_user(guild.owner_id)

            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        "## 📥 Guild Added\n"
                        "OnlyOneMessage has been *added* to a guild."
                    ), accessory=discord.ui.Thumbnail(media=(guild.icon.url if guild.icon else "https://cdn.monobyte.studio/onlyonemessageweb/logos/logoanimated.gif"))
                )
            )

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))

            container.add_item(
                discord.ui.TextDisplay(
                    f"**Guild Name:** `{guild.name}` (ID: `{guild.id}`)\n"
                    f"**Guild Owner:** `{guild_owner}` (ID: `{guild.owner.id}`)\n"
                    f"**Creation Date:** `{guild.created_at.strftime('%B %d, %Y')}`\n"
                    f"**Total Members:** `{guild.member_count}`"
                )
            )

            view.add_item(container)
            logchannel = self.bot.get_channel(guildjoinchannel)
            if not logchannel:
                logmsg("ERROR", f"Guild join log channel with ID {guildjoinchannel} was not found. Please check the configuration.", 
                       guild=str(guild.id), function="on_guild_join")
                return

            await logchannel.send(view=view)
            logmsg("DEBUG", "Log message successfully sent for on_guild_join", 
                guild=str(guild.id), function="on_guild_join")


        except Exception as e:
            logmsg("WARNING", f"An error occurred in on_guild_join: {e}", 
                   guild=str(guild.id), function="on_guild_join")
            event("GuildJoinError") # common failure point, track in analytics

async def setup(bot):
    await bot.add_cog(GuildJoin(bot))