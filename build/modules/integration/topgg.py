import requests
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from essential.metadata import devBranch
from essential.logging import logmsg
import asyncio

class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        load_dotenv(dotenv_path=os.path.join("data", ".env"))
        self.topgg_token = os.getenv('TOPGG_TOKEN')

        # only start the loop if top.gg support is enabled and a token is provided
        if not self.updatetopgg.is_running() and self.topgg_token and not devBranch:
            self.updatetopgg.start()
        
        else:
            logmsg("WARNING", "Top.gg updates will not be posted due to set configuration. To change this, edit the bot's metadata and/or environment variables.", 
                   function="topgg")


    @tasks.loop(minutes=30)
    async def updatetopgg(self):
        url = f"https://top.gg/api/bots/{self.bot.user.id}/stats"
        headers = {
            "Authorization": self.topgg_token,
            "Content-Type": "application/json"
        }
        data = {
            "server_count": len(self.bot.guilds)
        }
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor( # run in a separate thread to avoid blocking the event loop
                None,
                lambda: requests.post(url, json=data, headers=headers)
            )
            if response.status_code == 200:
                logmsg("INFO", f"Successfully updated top.gg: {data['server_count']} guilds posted", function="updatetopgg")
            else:
                logmsg("ERROR", f"Failed to update top.gg. HTTP Status: {response.status_code}", function="updatetopgg")
                logmsg("ERROR", response.text)

        except requests.RequestException as e:
            logmsg("ERROR", f"Error sending request to top.gg: {e}")

async def setup(bot):
    await bot.add_cog(TopGG(bot))