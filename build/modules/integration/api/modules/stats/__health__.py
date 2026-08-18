from flask import jsonify
from modules.integration.api.init import trackAPIrequest

def register(app, bot):
    @app.route("/v1/health")
    def health():
        # database
        database = "unknown"
        try:
            bot.database.command("ping")
            database = "online"
        except:
            database = "offline"

        # shard info
        shards = {}
        for shard_id, shard in bot.shards.items():
            latency = shard.latency or 0

            # calculate shard status based on latency
            if latency == 0:
                shard_status = "offline"
            elif latency > 0.5:
                shard_status = "degraded"

            else:
                shard_status = "online"

            shards[shard_id] = {
                "status": shard_status,
                "latency": round(latency, 4),

                "guilds": len([g for g in bot.guilds if g.shard_id == shard_id]),
                "members": sum(g.member_count or 0 for g in bot.guilds if g.shard_id == shard_id),
                "channels": sum(len(g.channels) for g in bot.guilds if g.shard_id == shard_id),
            }


        # degraded if any shard is degraded or offline, or if database is offline
        slow = any(s["status"] == "degraded" for s in shards.values())
        offline = any(s["status"] == "offline" for s in shards.values())
        database_down = database == "offline" # if database is offline

        health_status = "degraded" if (slow or offline or database_down) else "online"

        trackAPIrequest(bot, "/v1/health", 200)
        return jsonify({
            "health": health_status,
            "database": database,

            "shards": shards
        }), 200