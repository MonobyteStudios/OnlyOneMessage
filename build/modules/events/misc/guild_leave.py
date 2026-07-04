import discord
from discord.ext import commands
from essential.metadata import guildjoinchannel, guildleavechannel, metricsLogging
from essential.logging import logmsg, event
from essential.checks import is_guild_flooding
from essential.data import remove_guild_data

class GuildLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if is_guild_flooding(guild.id):
            logmsg("WARNING", f"Guild {guild.name} ({guild.id}) exceeded event rate limit.", 
                   guild=str(guild.id), function="on_guild_remove")
            
            event("RateLimited")
            return
        
        if not metricsLogging:
            logmsg("WARNING", "Metrics collection is disabled due to set configuration. To change this, edit the bot's metadata.", 
                   function="on_guild_remove")
            return
        

        logmsg("DEBUG", "on_guild_remove triggered", 
               guild=str(guild.id), function="on_guild_remove")
        

        guild_owner = guild.owner

        view = discord.ui.LayoutView(timeout=None)
        container = discord.ui.Container()

        container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    "## ❌ Guild Removed\n"
                    "OnlyOneMessage has been *removed* from a guild."
                ), accessory=discord.ui.Thumbnail(media=(guild.icon.url if guild.icon else "https://cdn.monobyte.studio/onlyonemessageweb/logos/logoanimated.gif"))
            )
        )

        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

        container.add_item(
            discord.ui.TextDisplay(
                f"**Guild Name:** `{guild.name}` (ID: `{guild.id}`)\n"
                f"**Guild Owner:** `{guild_owner}` (ID: `{guild.owner.id}`)\n"
                f"**Creation Date:** `{guild.created_at.strftime('%B %d, %Y')}`\n"
                f"**Total Members:** `{guild.member_count}`"
            )
        )

        view.add_item(container)
        logchannel = self.bot.get_channel(guildleavechannel)
        if not logchannel:
            logmsg("ERROR", f"Guild leave log channel with ID {guildleavechannel} was not found. Please check the configuration.", 
                   guild=str(guild.id), function="on_guild_remove")
            return

        await logchannel.send(view=view)
        logmsg("DEBUG", "Log message successfully sent for on_guild_remove", 
               guild=str(guild.id), function="on_guild_remove")


        remove_guild_data(self.bot, guild.id) # remove guild data from the database


async def setup(bot):
    await bot.add_cog(GuildLeave(bot))