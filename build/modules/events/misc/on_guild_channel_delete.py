import discord
from discord.ext import commands
from essential.logging import logmsg
from essential.checks import is_guild_flooding

class OnGuildChannelDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverdata = self.bot.serverdata


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if is_guild_flooding(channel.guild.id):
            logmsg("WARNING", f"Guild {channel.guild.name} ({channel.guild.id}) exceeded event rate limit.", 
                   guild=str(channel.guild.id), function="on_guild_channel_delete")
            return
        logmsg("DEBUG", "on_guild_channel_delete fired", 
               guild=str(channel.guild.id), function="on_guild_channel_delete")
        

        guild_id = channel.guild.id
        channel_id = str(channel.id)

        # delete the channel from the database
        updated = self.serverdata.update_one(
            {"_id": guild_id},
            {"$unset": {f"channels.{channel_id}": ""}}
        )
        if updated.modified_count: # if a document was modified, log the deletion
            logmsg("DEBUG", f"Removed deleted channel {channel_id} from database",
                guild=str(guild_id), function="on_guild_channel_delete")


async def setup(bot):
    await bot.add_cog(OnGuildChannelDelete(bot))