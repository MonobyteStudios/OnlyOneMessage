from essential.logging import logmsg
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

def parseSecret() -> Fernet:
    load_dotenv(dotenv_path=os.path.join("data", ".env"))
    secret = os.getenv("FERNET_SECRET")

    if not secret:
        secret = Fernet.generate_key().decode()
        with open(os.path.join("data", ".env"), "a") as f:
            f.write(f"\n\n# Auto-generated encryption key; do not change!\nFERNET_SECRET={secret}\n")
        os.environ["FERNET_SECRET"] = secret

        logmsg("NOTICE", "A fernet secret has been automatically generated and put in /data/.env. do NOT change this!",
               function="parseSecret")
        
    return Fernet(secret.encode())

fernet = parseSecret()

def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str | None:
    if not value:
        return None
    
    return fernet.decrypt(value.encode()).decode()






def create_guild_data(bot, guild_id):
    serverdata = bot.serverdata.find_one({"_id": guild_id})

    insertdata = { # default data structure for guilds
        "_id": guild_id,

        "channels": {},
        "config": {
            "stats": {},
            "functions": True,
            "loggingchannel": None,
            "loggingchannelid": 0,
            "loggingcategories": [
                "blacklist",
                "unblacklist",
                "deletions",
                "config"
            ],
        }
    }

    if not serverdata:
        bot.serverdata.insert_one(insertdata)
        logmsg("DEBUG", f"Created server data for guild ID {guild_id}",
                guild=str(guild_id), function="create_guild_data")
        return
    

    # merge existing data
    def merge_dict(target, defaults):
        for key, value in defaults.items():
            if key not in target:
                target[key] = value

            elif isinstance(value, dict) and isinstance(target[key], dict):
                merge_dict(target[key], value)  # recursive merge for nested dicts


    merge_dict(serverdata, insertdata)
    bot.serverdata.replace_one({"_id": guild_id}, serverdata) # update with merged data

    logmsg("DEBUG", f"Updated missing server fields for guild ID {guild_id}", 
           guild=str(guild_id), function="create_guild_data")
    


def remove_guild_data(bot, guild_id):
    serverdata = bot.serverdata.find_one({"_id": guild_id})
    if serverdata:
        bot.serverdata.delete_one({"_id": guild_id})
        logmsg("DEBUG", f"Removed server data for guild ID {guild_id}",
                guild=str(guild_id), function="remove_guild_data")
        
    else:
        logmsg("WARNING", f"There is no server data to remove for guild ID {guild_id}",
                guild=str(guild_id), function="remove_guild_data")