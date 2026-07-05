import discord
from discord.ext import commands
from datetime import timedelta
import time
from essential.checks import is_guild_flooding
from essential.logging import logmsg, event


def update_stat(bot, stat_key: str, guild): # adds stat
    # increment server count
    bot.serverdata.update_one(
        {"_id": guild.id},
        {"$inc": {f"config.stats.{stat_key}": 1}},
        upsert=True
    )
    logmsg("DEBUG", f"Server stat {stat_key} incremented by 1",
            function="update_stat", guild=str(guild.id))


    # increment global count
    bot.globaldata.update_one(
        {"_id": "global"},
        {"$inc": {stat_key: 1}},
        upsert=True
    )
    logmsg("DEBUG", f"Global stat {stat_key} incremented by 1",
            function="update_stat", guild=str(guild.id))




class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverdata = self.bot.serverdata

        self.cooldowntime = 2
        self.guild_cooldowns = {}  # {guild_id: last_action_time}

        self.msgspill = set()



    def check_cooldown(self, guild_id: int): # helper function for determining if a guild is in cooldown
        current = time.time()
        last = self.guild_cooldowns.get(guild_id, 0)
        elapsed = current - last

        if elapsed >= self.cooldowntime:
            return True, 0.0     # allowed to continue
        
        else:
            return False, self.cooldowntime - elapsed # still in cooldown, return remaining time
        



    async def react_withdelay(self, message, emoji):
        guild_id = message.guild.id
        allowed, remaining = self.check_cooldown(guild_id)

        serverdata = self.serverdata.find_one({"_id": guild_id}) or {}
        channeldata = serverdata.get("channels", {}).get(str(message.channel.id), {})

        reactions = channeldata.get("reactions", False)
        if not reactions:
            logmsg("DEBUG", "Reactions are disabled for this channel, skipping react_withdelay",
                   guild=str(guild_id), function="react_withdelay")
            return
        

        if allowed:
            await message.add_reaction(emoji)
            self.guild_cooldowns[guild_id] = time.time()

            logmsg("DEBUG", f"Added reaction to message successfully",
                     guild=str(guild_id), function="react_withdelay")
            
        else:
            logmsg("DEBUG", f"Cooldown is active, skipping reaction. {remaining} seconds remaining.",
                   guild=str(guild_id), function="react_withdelay")
            

    
    async def send_error(self, message, title: str, description: str):
        guild_id = message.guild.id
        allowed, remaining = self.check_cooldown(guild_id)

        # use react_with_delay to indicate error
        await self.react_withdelay(message, "❌")
        
        view = discord.ui.LayoutView()
        container = discord.ui.Container()

        container.add_item(
            discord.ui.TextDisplay(
                f"## {title}\n"
                f"{description}"
            )
        )
        view.add_item(container)


        if allowed:
            await message.reply(view=view)
            self.guild_cooldowns[guild_id] = time.time()

            logmsg("DEBUG", "Successfully set error embed",
                   guild=str(guild_id), function="send_error")
            
        else:
            logmsg("DEBUG", f"Cooldown is active, skipping error message. {remaining} seconds remaining.",
                   guild=str(guild_id), function="send_error")






    async def add_durations(self, guild_id: int, channel_id: int, member_id: int): # add a member to a guilds durations
        logmsg("DEBUG", "add_duration function called",
            guild=str(guild_id), function="add_durations")

        current_time = time.time()
        serverdata = self.serverdata.find_one({"_id": guild_id}) or {}
        if not serverdata:
            return

        duration = serverdata.get("channels", {}).get(str(channel_id), {}).get("cooldown", 0)
        if duration != 0:
            expire_time = current_time + duration # calculate expiration time via delta

            self.serverdata.update_one(
                {"_id": guild_id},
                {"$set": {f"channels.{str(channel_id)}.cooldown_cache.{str(member_id)}": int(expire_time)}}
            )
            logmsg("DEBUG", f"Added member {member_id} to durations database with expiration time {expire_time}",
                guild=str(guild_id), function="add_durations")
            
            

                


    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or isinstance(message.channel, discord.channel.DMChannel) or message.author.bot:
            return
        
        if is_guild_flooding(message.guild.id):
            logmsg("WARNING", f"Guild {message.guild.name} ({message.guild.id}) exceeded event rate limit.", 
                    guild=str(message.guild.id), function="on_message")
            
            event("RateLimited")
            return


        
        logmsg("DEBUG", f"on_message event executed",
                guild=str(message.guild.id), function="on_message")

        perms = message.channel.permissions_for(message.author)
        serverdata = self.serverdata.find_one({"_id": message.guild.id}) or {}
        channeldata = serverdata.get("channels", {}).get(str(message.channel.id), {})
        
        configdata = serverdata.get("config", {})
        if configdata.get('functions') is False:
            logmsg("DEBUG", "Functionality is disabled for this guild, returning", 
                   guild=str(message.guild.id), function="on_message")
            return



        if not channeldata: # if the channel isnt registered, return
            logmsg("DEBUG", f"Channel {message.channel.id} is not registered for OnlyOneMessage, returning", 
                    guild=str(message.guild.id), function="on_message")
            return
        logmsg("DEBUG", "Message is in a OnlyOneMessage channel", 
            guild=str(message.guild.id), function="on_message")



        blacklistrole = discord.utils.get(message.guild.roles, id=channeldata.get("blacklist_role", 0))
        if not blacklistrole:
            await self.send_error(
                message,
                title="❌ Event Error",
                description=f"The slowmode role for this channel does not exist. Please run `/addchannel` again to fix channel configuration."
            )
            logmsg("DEBUG", "Unable to blacklist; respective role does not exist", 
                guild=str(message.guild.id), function="on_message")
            return
        
        
        
        # message spilling handler
        if message.author.id in self.msgspill:
            logmsg("DEBUG", "Message is in message spill", 
                guild=str(message.guild.id), function="on_message")


            if isinstance(message.author, discord.Member) and not perms.bypass_slowmode and not perms.administrator: # make sure the user isnt an admin
                try:  
                    await message.delete()  # Remove spill messages
                    logmsg("DEBUG", "Deleted spill message successfully", 
                        guild=str(message.guild.id), function="on_message")

                except discord.Forbidden:
                    logmsg("WARNING", "Failed to delete message: Forbidden", 
                        guild=str(message.guild.id), function="on_message")
                return
            
        if not blacklistrole in message.author.roles:
            self.msgspill.add(message.author.id)
            logmsg("DEBUG", "Added user to msgspill log", 
                guild=str(message.guild.id), function="on_message")
            



        if perms.bypass_slowmode or perms.administrator: # if the user has perms to bypass slowmode
            event("MessageWhitelisted")
            update_stat(self.bot, "totalwhitelists", message.guild)
            
            try:
                await self.react_withdelay(message, "😇") # whitelist indication

            except:
                logmsg("DEBUG", "unable to add reaction, continuing", 
                    guild=str(message.guild.id), function="on_message")
                
            logmsg("DEBUG", "User is whitelisted, event cancelled", 
                guild=str(message.guild.id), function="on_message")
            return
        
        
        else: # person does NOT have the whitelist role
            try:
                logmsg("DEBUG", "Attempting to blacklist user", 
                    guild=str(message.guild.id), function="on_message")


                if not blacklistrole in message.author.roles:                                    
                    await message.author.add_roles(
                        blacklistrole, 
                        reason=f"OnlyOneMessage slowmode restriction for {message.author.display_name}"
                    )

                    update_stat(self.bot, "totalblacklists", message.guild)
                    await self.add_durations(message.guild.id, message.channel.id, message.author.id)
                    event("MessageBlacklisted")

                    logmsg("DEBUG", "Attempt Successful", 
                        guild=str(message.guild.id), function="on_message")

                else:
                    logmsg("DEBUG", "User already has role", 
                        guild=str(message.guild.id), function="on_message")
                    
                    
                try: 
                    await self.react_withdelay(message, "⛈️") # blacklist indication
                    
                except Exception as e:
                    logmsg("DEBUG", f"unable to add reaction, continuing", 
                        guild=str(message.guild.id), function="on_message")




            except discord.Forbidden: # bot doesnt have perms
                clientbot = await message.guild.fetch_member(self.bot.user.id)
                clientrole = clientbot.top_role

                if clientrole.position < blacklistrole.position: # is the blacklist role above the bots role
                    await self.send_error(
                        message,
                        title="❌ I don't have permission!",
                        description=f"The <@&{blacklistrole.id}> role is higher than the bot's role, preventing OnlyOneMessage from restricting this user. "
                                    "Please try again when you fix this issue."
                    )
                    logmsg("DEBUG", f"Unable to blacklist; role is above bot role",
                            guild=str(message.guild.id), function="on_message")

                else:
                    if not clientbot.guild_permissions.manage_roles:
                        await self.send_error(
                            message,
                            title="❌ I don't have permission!",
                            description=f"OnlyOneMessage is missing the `Manage Roles` permission, preventing me from blacklisting this user. "
                                        "Please try again when you fix this issue."
                        )
                        logmsg("DEBUG", f"Unable to add role, missing permissions",
                                guild=str(message.guild.id), function="on_message")


            except Exception as e:
                await self.send_error(
                    message,
                    title="❌ Unknown Error",
                    description=f"OnlyOneMessage encountered an unknown error while trying to blacklist this user. This error has already been logged; no action is needed."
                )
                logmsg("ERROR", f"Unexpected error in on_message: {e}",
                    guild=str(message.guild.id), function="on_message")



        if message.author.id in self.msgspill: # remove user from spill after processing
            await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=1)) # wait a bit until removing the user

            self.msgspill.discard(message.author.id)
            logmsg("DEBUG", f"Removed {message.author.id} from message spill", 
                guild=str(message.guild.id), function="on_message")


async def setup(bot):
    await bot.add_cog(OnMessage(bot))