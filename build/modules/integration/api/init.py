from discord.ext import commands
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from threading import Thread
from flask_cors import CORS
from waitress import serve
import importlib
import os
import socket

from essential.logging import logmsg
from modules.integration.metrics import Metrics
from essential.metadata import apiSupported


def isPortinUse(port: int): # check if a port is in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def trackAPIrequest(bot, endpoint: str, status: int):
    logmsg("DEBUG", f"Responded to API request at endpoint: {endpoint} with status: {status}", 
           function="api")
    
    metricscog: Metrics = bot.get_cog("Metrics")
    if metricscog and metricscog.apiusage:
        metricscog.apiusage.labels(endpoint=endpoint, status=status).inc()



class API(commands.Cog):
    thread = None
    instance = None

    def __init__(self, bot, port: int = 9300):
        self.bot = bot
        self.port = port

        if not apiSupported:
            logmsg("WARNING", "The OOM API is disabled due to set configuration. To change this, edit the bot's metadata.", 
                   function="api")
            return

        self.api = Flask(__name__)
        CORS(self.api, resources={r"/v1/*": {"origins": "*"}})

        self.limiter = Limiter(
            get_remote_address,
            app=self.api,
            storage_uri="memory://",  # memory is fine to use in this situation
            default_limits=["30 per minute"]
        )

        # load API modules dynamically
        base_path = os.path.join(os.path.dirname(__file__), "modules") # route to the modules folder

        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if filename.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, filename), os.path.dirname(__file__))
                    module_name = rel_path.replace(os.path.sep, ".")[:-3]  # remove .py
                    module_name = f"{__package__}.{module_name}"  # add package prefix

                    # load the module & call its function
                    try:
                        mod = importlib.import_module(module_name)
                        if hasattr(mod, "register"):
                            mod.register(self.api, self.bot)
                        logmsg("INFO", f"Loaded API module: {filename}", 
                               function="api")

                    except Exception as e:
                        logmsg("ERROR", f"Failed to load API module {filename}: {e}", 
                               function="api")


        # start the API thread, if the port is not already in use
        if isPortinUse(self.port):
            logmsg("WARNING", f"Port {self.port} is already in use, API will not start.", 
                   function="api")

        else:
            self.start_thread()


    def start_thread(self):
        API.instance = self.api
        API.thread = Thread(target=self.runapi, daemon=True)
        API.thread.start()
        logmsg("INFO", f"The OnlyOneMessage API is now active at port {self.port}.", function="api")

    def runapi(self):
        serve(self.api, host="0.0.0.0", port=self.port)


async def setup(bot):
    await bot.add_cog(API(bot))