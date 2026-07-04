import discord
from discord.ext import commands, tasks
from essential.logging import logmsg
import random

class UpdatePresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not self.change_presence.is_running():
            self.change_presence.start()

    def get_users(self):
        return sum(guild.member_count for guild in self.bot.guilds)
        

    @tasks.loop(seconds=30)
    async def change_presence(self):
        try:
            global_data = self.bot.globaldata.find_one({"_id": "global"}) or {}
            whitelists = global_data.get("totalwhitelists", 0)
            blacklists = global_data.get("totalblacklists", 0)
            total_messages = whitelists + blacklists

            status_messages = [
                f"{len(self.bot.guilds):,} servers 💭",
                f"{self.get_users():,} members 💭",
                f"{whitelists:,} bypassed messages 💭",
                f"{blacklists:,} restricted messages 💭",
                f"{total_messages:,} global messages 💭",
                "/help 💭",
                "the ticking clock 💭",
                "the silence 💭",
            ]

            current_status = random.choice(status_messages)
            await self.bot.change_presence(
                activity=discord.CustomActivity(name=f"Listening to {current_status}")
            )

        except Exception as e:
            logmsg("ERROR", f"Error updating presence: {e}", 
                   function="presence")


    @commands.Cog.listener()
    async def on_resumed(self):
        logmsg("DEBUG", "Bot session resumed. Restarting presence loop.", function="presence")
        self.change_presence.restart()


async def setup(bot):
    await bot.add_cog(UpdatePresence(bot))
