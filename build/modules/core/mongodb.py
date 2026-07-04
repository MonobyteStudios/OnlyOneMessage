from discord.ext import commands
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from essential.metadata import devBranch
from essential.logging import logmsg
from dotenv import load_dotenv

class mongoDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.database = self.database
        
        self.bot.globaldata = self.globaldata
        self.bot.serverdata = self.serverdata
        

    PRODUCTION = False if devBranch else True
    load_dotenv(dotenv_path=os.path.join("data", ".env")) # load env file

    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DEV_DB = os.getenv('MONGO_DEV_DB')
    MONGO_PROD_DB = os.getenv('MONGO_PROD_DB')

    # connect to mongo
    mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    try:
        mongo_client.admin.command('ping')
        logmsg("DEBUG", "Successfully connected to MongoDB!", function="mongodb")

    except Exception as e:
        logmsg("ERROR", f"An error has occurred connecting to MongoDB:\n{e}", function="mongodb")


    db_name = MONGO_PROD_DB if PRODUCTION else MONGO_DEV_DB
    logmsg("NOTICE", f"OnlyOneMessage is using the '{db_name}' database. If this is incorrect, please terminate this process and edit 'PRODUCTION' in mongodb.py.", 
           function="mongodb")


    database = mongo_client[db_name]
    globaldata = database["globaldata"]
    serverdata = database["serverdata"] 


async def setup(bot):
    await bot.add_cog(mongoDB(bot))
