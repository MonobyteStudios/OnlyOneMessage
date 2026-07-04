import discord
from discord.ext import commands
from discord import app_commands

from essential.checks import guild_only
from essential.logging import logmsg
from essential.metadata import getvar

import sys
import time
import datetime
import math
from importlib.metadata import version
import psutil

class InviteStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="invite", description="Invite OnlyOneMessage to your own server")  # Invite command
    @guild_only()
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.channel_id))
    async def invite(self, interaction: discord.Interaction):
        logmsg("DEBUG", "/invite executed", 
               guild=str(interaction.guild.id), function="invite")
        
        await interaction.response.send_message("Invite OnlyOneMessage to your server here!\nhttps://discord.com/oauth2/authorize?client_id=1258462729602203768", ephemeral=True)



    class StatsView(discord.ui.LayoutView):
        def __init__(self, bot, guild):
            super().__init__(timeout=None)
            self.bot = bot
            self.serverdata = self.bot.serverdata
            self.globaldata = self.bot.globaldata

            def convert_size(size_bytes):
                if size_bytes == 0:
                    return "0B"
                
                size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                i = int(math.floor(math.log(size_bytes, 1024)))
                p = math.pow(1024, i)
                s = round(size_bytes / p, 2)
                return "%s %s" % (s, size_name[i])


            # global counts
            global_data = self.globaldata.find_one({"_id": "global"}) or {}
            whitelists = global_data.get("totalwhitelists", 0) or 0
            blacklists = global_data.get("totalblacklists", 0) or 0
            totalmsgs = int(whitelists) + int(blacklists)


            startTime = getattr(bot, "StartTime", None)
            uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))
            start_timestamp = f"<t:{int(startTime)}:f>"


            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    "# 📊 Statistics \n"
                    "*View global & server statistics about OnlyOneMessage.*"
                )
            )

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))


            container.add_item(
                discord.ui.TextDisplay(
                    "### 🤖 Bot Information\n"

                    f"Version: `{getvar('version', "metadata.json") or 'N/A'} [{getvar('build', "metadata.json") or 'N/A'}]`\n"
                    f"Uptime: `{uptime}` ({start_timestamp})\n"
                    f"Latency: `{round(bot.latency * 1000, 2)}ms`\n"
                    f"Shard Info: `{f'Shard {guild.shard_id} / {bot.shard_count} Total Shards' if guild else 'N/A'}`\n"
                    f"Servers: `{len(bot.guilds)}`\n"
                    f"Global Members: `{sum(g.member_count for g in bot.guilds):,}`" 
                ))

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    "### 📈 Usage Statistics\n"

                    f"Total Messages: `{totalmsgs:,}`\n"
                    f"Restricted Messages: `{blacklists:,}`\n"
                    f"Bypassed Messages: `{whitelists:,}`"
                )
            )


            # personalized server stats
            serverdata = self.serverdata.find_one({"_id": guild.id}) or {}
            stats = serverdata.get("config", {}).get("stats", {})
            if stats:
                channels = serverdata.get("channels", {})
                serverblacklists = stats.get("totalblacklists", 0)
                serverwhitelists = stats.get("totalwhitelists", 0)
                servermessages = int(serverblacklists) + int(serverwhitelists)

                container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

                container.add_item(
                    discord.ui.TextDisplay(
                        "### 🛡️ Guild Metrics\n"

                        f"Managed Channels (`{len(channels)}`): {', '.join(f'<#{cid}>' for cid in list(channels.keys())[:10])}{'...' if len(channels) > 10 else ''}\n"
                        f"Total Messages: `{servermessages:,}`\n"
                        f"Restricted Messages: `{serverblacklists:,}`\n"
                        f"Bypassed Messages: `{serverwhitelists:,}`\n"
                        "-# This category is personalized for this server"

                    )
                )
            

            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

            container.add_item(
                discord.ui.TextDisplay(
                    "### 💻 Server Performance\n"

                    f"CPU Usage: `{psutil.cpu_percent()}%`\n"

                    f"Memory Usage: `{psutil.virtual_memory().percent}%` "
                    f"(`{convert_size(psutil.virtual_memory().used)}` / `{convert_size(psutil.virtual_memory().total)}`)\n"
                    
                    f"Disk Usage: `{psutil.disk_usage('/').percent}%` "
                    f"(`{convert_size(psutil.disk_usage('/').used)}` / `{convert_size(psutil.disk_usage('/').total)}`)\n"
                ))
            
            container.add_item(discord.ui.Separator())

            container.add_item(
                discord.ui.TextDisplay(
                    f"Python Version: `{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`\n"
                    f"Discord.py Version: `{version('discord.py')}`\n\n"
                ))


            self.add_item(container)



    @app_commands.command(name="stats", description="View global & server statistics about OnlyOneMessage")
    @guild_only()
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.channel_id))
    async def stats(self, ctx: discord.Interaction):
        logmsg("DEBUG", "/stats executed", 
               guild=str(ctx.guild.id), function="stats")

        await ctx.response.send_message(view=self.StatsView(self.bot, ctx.guild))




async def setup(bot):
    await bot.add_cog(InviteStats(bot))