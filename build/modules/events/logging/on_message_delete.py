import discord
import aiohttp
from discord.ext import commands
from essential.checks import is_guild_flooding
from essential.logging import logmsg, event
from essential.data import decrypt

class OnMessageDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverdata = self.bot.serverdata


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if is_guild_flooding(message.guild.id):
            logmsg("WARNING", f"Guild {message.guild.name} ({message.guild.id}) exceeded event rate limit.", 
                   guild=str(message.guild.id), function="on_message_delete")
            
            event("RateLimited")
            return
        


        channel = message.channel
        logmsg("DEBUG", "message deletion detected", 
               guild=str(message.guild.id), function="on_message_delete")


        unblacklisted = False
        serverdata = self.serverdata.find_one({"_id": message.guild.id}) or {}
        channeldata = serverdata.get("channels", {}).get(str(channel.id), None)

        blacklistrole = discord.utils.get(message.guild.roles, id=channeldata.get("blacklist_role", None))
        if not blacklistrole:
            return
        

        if not message.author.bot and message.guild and serverdata and channeldata:
            logmsg("DEBUG", "message is in OOM channel", 
                    guild=str(message.guild.id), function="on_message_delete")
            
            if channeldata.get("recovery", True):
                if message.author.id in getattr(self.bot.get_cog("OnMessage"), "msgspill", None): # make sure the message isnt in spill (prevents duplicate logs and actions)
                    logmsg("DEBUG", "Member in msgspill, event cancelled", 
                            guild=str(message.guild.id), function="on_message_delete")
                    return
            
                if blacklistrole in message.author.roles:
                    try:
                        await message.author.remove_roles(blacklistrole)
                        logmsg("DEBUG", "Successfully removed role from user", 
                                guild=str(message.guild.id), function="on_message_delete")
                        
                        unblacklisted = True

                    except Exception as e:
                        logmsg("DEBUG", f"Failed to remove blacklist role from user: {e}", 
                                guild=str(message.guild.id), function="on_message_delete")
                        


            webhookurl = decrypt(serverdata.get("config", {}).get("loggingchannel"))
            if webhookurl:
                loggingcategories = serverdata.get("config", {}).get("loggingcategories")
                if loggingcategories and "deletions" not in loggingcategories:
                    logmsg("DEBUG", "Config logging category disabled, skipping logconfig",
                        guild=str(message.guild.id), function="on_message_delete")
                    return


                embed = discord.Embed(
                    title="❌ Message Deleted",
                    description=f"A message has been deleted in {channel.mention}.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📝 Details",
                    value=f"**Author**: <@{message.author.id}> (ID: `{message.author.id}`)\n",
                    inline=False
                )
                embed.add_field(
                    name="🔒 Slowmode Removed?",
                    value="✅ Yes" if unblacklisted else "❌ No",
                    inline=False
                )
                embed.timestamp = discord.utils.utcnow()
                if message.author.avatar:
                    embed.set_thumbnail(url=message.author.avatar.url)


                try:
                    async with aiohttp.ClientSession() as session:
                        webhook = discord.Webhook.from_url(webhookurl, session=session)
                        await webhook.send(embed=embed)

                    logmsg("DEBUG", "Logging message sent successfully!",
                        guild=str(message.guild.id), function="on_message_delete")
                    
                except (discord.NotFound, discord.Forbidden) as e:
                    logmsg("DEBUG", f"Cannot send log: {e}",
                        guild=str(message.guild.id), function="on_message_delete")

async def setup(bot):
    await bot.add_cog(OnMessageDelete(bot))