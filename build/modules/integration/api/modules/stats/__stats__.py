from flask import jsonify
from essential.metadata import VERSION, BUILD
import time

from modules.integration.api.init import trackAPIrequest

def register(app, bot):
        @app.route("/v1/stats")
        def stats():
            total_guilds = len(bot.guilds)
            total_members = sum(g.member_count or 0 for g in bot.guilds)
            total_channels = sum(len(g.channels) for g in bot.guilds)

            startTime = getattr(bot, "StartTime", None)
            uptime = round(time.time() - startTime)

            global_data = bot.globaldata.find_one({"_id": "global"}) or {}
            whitelists = global_data.get("totalwhitelists", 0)
            blacklists = global_data.get("totalblacklists", 0)
            totalmsgs = whitelists + blacklists

            trackAPIrequest(bot, "/v1/stats", 200)
            return jsonify({
                "version": VERSION,
                "build": BUILD,
                "latency": round(bot.latency * 1000, 2),
                "uptime": uptime,
                "shards": bot.shard_count,

                "guilds": total_guilds,
                "members": total_members,
                "channels": total_channels,

                "whitelists": whitelists,
                "blacklists": blacklists,
                "totalmsgs": totalmsgs
            }), 200