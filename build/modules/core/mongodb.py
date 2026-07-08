from discord.ext import commands
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from essential.logging import logmsg
from dotenv import load_dotenv

class mongoDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.database = self.database
        
        self.bot.globaldata = self.globaldata
        self.bot.serverdata = self.serverdata
        
    load_dotenv(dotenv_path=os.path.join("data", ".env")) # load env file
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB = os.getenv('MONGO_DB')

    # connect to mongo
    mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    try:
        mongo_client.admin.command('ping')
        logmsg("DEBUG", "Successfully connected to MongoDB!", function="mongodb")

    except Exception as e:
        logmsg("ERROR", f"An error has occurred connecting to MongoDB:\n{e}", function="mongodb")


    database = mongo_client[MONGO_DB]
    globaldata = database["globaldata"]
    serverdata = database["serverdata"] 


async def setup(bot):
    await bot.add_cog(mongoDB(bot))
