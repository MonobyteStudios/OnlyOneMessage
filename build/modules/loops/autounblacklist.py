import discord
import time
from essential.logging import logmsg
from discord.ext import commands, tasks

class loops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverdata = self.bot.serverdata

        if not self.duration_check.is_running():
            self.duration_check.start()


    @tasks.loop(seconds=10)
    async def duration_check(self):
        current_time = time.time()

        for guild_data in self.serverdata.find({"channels": {"$exists": True}}): # guild data with channels field
            guild_id = guild_data["_id"]
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            channels = guild_data.get("channels", {})
            if not channels:
                continue


            for channel_id, channel_data in channels.items(): # every configured channel
                cooldown_cache = channel_data.get("cooldown_cache", {})
                if not cooldown_cache:
                    continue

                blacklist_role_id = channel_data.get("blacklist_role", 0)
                blacklist_role = discord.utils.get(guild.roles, id=int(blacklist_role_id))
                if not blacklist_role:
                    continue


                removedata = []
                for memberid, expiry in cooldown_cache.items(): # every member in cooldown cache
                    member_id = int(memberid)
                    member = guild.get_member(member_id)

                    if not member: # the member does not exist
                        removedata.append(memberid)
                        logmsg("DEBUG", f"Member ID {memberid} not found in guild, removing from cooldown cache",
                                guild=str(guild_id), function="duration_check")
                        continue


                    elif blacklist_role not in member.roles: # the member doesnt even have the blacklist role
                        removedata.append(memberid)
                        logmsg("DEBUG", f"Member {memberid} does not have blacklist role for channel {channel_id}, removing from cooldown cache",
                                guild=str(guild_id), function="duration_check")
                        continue

                    if current_time >= expiry: # cooldown expired, remove role
                        logmsg("DEBUG", f"Cooldown expired for member {memberid} in channel {channel_id}, removing blacklist role",
                                guild=str(guild_id), function="duration_check")
                        removedata.append(memberid)

                        try:
                            await member.remove_roles(blacklist_role, reason="Cooldown expired for this member")

                        except discord.Forbidden:
                            logmsg("WARNING", f"Failed to remove blacklist role from member {memberid} in channel {channel_id}: Forbidden",
                                    guild=str(guild_id), function="duration_check")



                if removedata: # is there anything to cleanup?
                    removefields = { # construct the $unset fields for mongodb query
                        f"channels.{channel_id}.cooldown_cache.{memberid}": ""
                        for memberid in removedata
                    }

                    self.serverdata.update_one(
                        {"_id": guild_id},
                        {"$unset": removefields}
                    )
                    
async def setup(bot):
    await bot.add_cog(loops(bot))
