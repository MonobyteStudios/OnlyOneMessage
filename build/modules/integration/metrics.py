from discord import Interaction, InteractionType, app_commands
from discord.ext import commands, tasks
from prometheus_client import start_http_server, Gauge, Counter, REGISTRY
import time
import os

from essential.logging import logmsg, event_usage

class Metrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        port = 9200
        PREFIX = "oom_"
        
        try:
            start_http_server(port)  # Prometheus endpoint (localhost:9200/metrics)
        except OSError:
            logmsg("DEBUG", "Endpoint already active, continuing...",
                   function="metrics")


        # safely init a metric
        def initmetric(metrictype, name: str, desc: str, labels: list[str] = None): 
            labels = labels or []

            existing = REGISTRY._names_to_collectors.get(name)
            if existing:
                return existing  # reuse it as it already exists

            try:
                return metrictype(name, desc, labels)
            
            except Exception:
                return None

        # basic
        self.guilds = initmetric(Gauge, PREFIX + "guilds", "Guilds OnlyOneMessage can access", ["shard"])
        self.channels = initmetric(Gauge, PREFIX + "channels", "Channels OnlyOneMessage can access", ["shard"])
        self.members = initmetric(Gauge, PREFIX + "members", "All members across all guilds", ["shard"])

        # connection
        self.latencies = initmetric(Gauge, PREFIX + "latencies", "Individual shard latency, in seconds", ["shard"])
        self.connection = initmetric(Gauge, PREFIX + "connection", "Shard connection state (1=connected, 0=disconnected)", ["shard"])

        # usage
        self.interactions = initmetric(Counter, PREFIX + "interactions", "Interactions members trigger", ["interaction"])
        self.uptime = initmetric(Gauge, PREFIX + "uptime", "Bot uptime in seconds")
        self.apiusage = initmetric(Counter, PREFIX + "api_requests", "API requests received", ["endpoint", "status"]) # this is incremented in api.py

        self.whitelists = initmetric(Gauge, PREFIX + "whitelists", "Total whitelisted users")
        self.blacklists = initmetric(Gauge, PREFIX + "blacklists", "Total blacklisted users")
        self.totalmessages = initmetric(Gauge, PREFIX + "totalmsgs", "Total messages processed")


        self.logpath = os.path.join("data", "log.log")
        self.lastlogline = 0
        self.logfrequency = initmetric(Gauge, PREFIX + "logfrequency", "Log frequency within the 2 minutes")


        if not self.update_metrics.is_running():
            self.update_metrics.start()
            
        if not self.update_logfrequency.is_running():
            self.update_logfrequency.start()

        logmsg("INFO", f"Prometheus is now active at port {port}.", 
               function="metrics")




    @tasks.loop(seconds=5)
    async def update_metrics(self):
        for shard_id, latency in self.bot.latencies: # per-shard stats
            shard_guilds = [g for g in self.bot.guilds if g.shard_id == shard_id]

            guild_count = len(shard_guilds)
            member_count = sum(g.member_count or 0 for g in shard_guilds)
            channel_count = sum(len(g.channels) for g in shard_guilds)

            self.guilds.labels(shard=str(shard_id)).set(guild_count)
            self.members.labels(shard=str(shard_id)).set(member_count)
            self.channels.labels(shard=str(shard_id)).set(channel_count)


            connected = 1 if (latency or 0) > 0 else 0 # 1 = connected, 0 = disconnected
            self.latencies.labels(shard=str(shard_id)).set(latency)
            self.connection.labels(shard=str(shard_id)).set(connected)


        for event_name, count in event_usage.items():
            self.interactions.labels(interaction=f"{event_name}").inc(count)
            event_usage[event_name] = 0  # reset, to prevent double-counting


        # static stats
        global_data = self.bot.globaldata.find_one({"_id": "global"}) or {}
        whitelists = global_data.get("totalwhitelists", 0) or 0
        blacklists = global_data.get("totalblacklists", 0) or 0

        self.whitelists.set(whitelists)
        self.blacklists.set(blacklists)
        self.totalmessages.set(whitelists + blacklists)

        startTime = getattr(self.bot, "StartTime", None)
        if startTime:
            uptime = int(time.time() - startTime)
            self.uptime.set(uptime)


    @tasks.loop(minutes=2)
    async def update_logfrequency(self):
        if os.path.exists(self.logpath):
            with open(self.logpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if self.lastlogline == 0:  # first run, dont do anything
                    self.lastlogline = len(lines)
                    return

                new_lines = len(lines) - self.lastlogline # new lines - old lines
                self.logfrequency.set(new_lines)
                self.lastlogline = len(lines) # update it to current amount





    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        interaction_type = interaction.type.name.lower()
        interaction_name = None

        if interaction.type == InteractionType.application_command and interaction.command:
            if isinstance(interaction.command, app_commands.Command): # the interaction is a command
                interaction_name = ""
                parent = interaction.command.parent

                while parent is not None:
                    interaction_name += parent.name + " "
                    parent = parent.parent
                interaction_name += interaction.command.name

            else:
                interaction_name = interaction.command.name
        else:
            # button, select menu, modal, etc.
            interaction_name = interaction_type

        interaction_name = interaction_name or "unknown"
        self.interactions.labels(interaction=interaction_name).inc()
        

async def setup(bot):
    await bot.add_cog(Metrics(bot))
