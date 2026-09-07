import discord
from discord.ext import commands
from essential.metadata import GUILD_LEAVE_CHANNEL
from essential.logging import logmsg
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
        
        logchannel = self.bot.get_channel(GUILD_LEAVE_CHANNEL)
        if not logchannel:
            return

        await logchannel.send(view=view)
        logmsg("DEBUG", "Log message successfully sent for on_guild_remove", 
               guild=str(guild.id), function="on_guild_remove")


        remove_guild_data(self.bot, guild.id) # remove guild data from the database


async def setup(bot):
    if GUILD_LEAVE_CHANNEL:
        await bot.add_cog(GuildLeave(bot))