import discord
import aiohttp
from discord.ext import commands
from datetime import timedelta
from essential.checks import is_guild_flooding
from essential.logging import logmsg, event
from essential.data import decrypt


async def sendlog(
    webhookurl: str,
    targetchannel: discord.TextChannel,
    after: discord.Member,
    restricted: bool,
    serverdata
):
    embed = discord.Embed(
        title=f"🎭 Member {'Restricted' if restricted else 'Unrestricted'}",
        description=f"A member of your server {'is now in slowmode' if restricted else 'is no longer in slowmode'} in {targetchannel.mention}.",
        color=discord.Color.red() if restricted else discord.Color.green()
    )
    embed.add_field(name="Author", value=f"<@{after.id}> (ID `{after.id}`)", inline=False)

    if restricted: # only if the member has been restricted
        await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=1))

        guildinfo = serverdata.find_one({"_id": after.guild.id})
        timestamp = guildinfo.get("channels", {}).get(str(targetchannel.id), {}).get("cooldown_cache", {}).get(str(after.id), None)
        
        if timestamp:
            embed.add_field(
                name="Slowmode expires",
                value=f"<t:{int(timestamp)}:R> (<t:{int(timestamp)}:F>)",
                inline=False
            )


    embed.timestamp = discord.utils.utcnow()
    if after.avatar:
        embed.set_thumbnail(url=after.avatar.url)

    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhookurl, session=session)
            await webhook.send(embed=embed)

        logmsg("DEBUG", "Logging message sent successfully!",
               guild=str(after.guild.id), function="on_member_update")
        
    except (discord.NotFound, discord.Forbidden) as e:
        logmsg("WARNING", f"Failed to send log: {e}",
               guild=str(after.guild.id), function="on_member_update")



class OnMemberUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverdata = self.bot.serverdata



    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.guild:
            if is_guild_flooding(after.guild.id):
                logmsg("WARNING", f"Guild {after.guild.name} ({after.guild.id}) exceeded event rate limit.",
                    guild=str(after.guild.id), function="on_member_update")
                
                event("RateLimited")
                return            
            logmsg("DEBUG", "on_member_update event fired",
                guild=str(after.guild.id), function="on_member_update")


            serverdata = self.serverdata.find_one({"_id": after.guild.id}) or {}
            channels = serverdata.get("channels", {})

            # get the channel the role is associated with
            changed_roles = set(before.roles) ^ set(after.roles)
            for role in changed_roles:
                action = role in after.roles  # True = blacklisted, False = unblacklisted

                for channel_id, data in channels.items():
                    if data.get("blacklist_role") == role.id: # if the role matches the channel's blacklist role
                        modifiedchannel = after.guild.get_channel(int(channel_id))
                        if modifiedchannel:
                            webhookurl = decrypt(serverdata.get("config", {}).get("loggingchannel"))
                            loggingcategories = serverdata.get("config", {}).get("loggingcategories")

                            # check if the logging category for this action is enabled
                            categorytocheck = "blacklist" if action else "unblacklist"
                            if not categorytocheck in loggingcategories:
                                logmsg("DEBUG", f"Config logging category '{categorytocheck}' disabled, skipping logconfig", 
                                       guild=str(after.guild.id), function="on_member_update")
                                return

                            if webhookurl:
                                await sendlog(
                                    webhookurl,
                                    modifiedchannel,
                                    after,
                                    action,
                                    self.serverdata
                                )
                                                    

            

async def setup(bot):
    await bot.add_cog(OnMemberUpdate(bot))