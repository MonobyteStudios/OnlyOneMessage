import time
from datetime import date
import logging.handlers
import os
from collections import Counter


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename=os.path.join("data", "log.log"),
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,
    backupCount=5,
)

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('{asctime} [ {levelname:<8} ] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)



def logmsg(status, message, guild: str = None, function: str = None):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    today = date.today()

    gray_color = "\033[90m"
    guild_color = "\033[38;5;136m"
    function_color = "\033[96m"
    reset = "\033[0m"
    bold = "\033[1m"

    status_colors = {
        "debug": "\033[94m",
        "info": "\033[92m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "notice": "\033[95m",
    }
    status_text = status.upper()
    status_color = status_colors.get(status.lower(), reset)

    log_entry = (
        f"{gray_color}{bold}{today} {current_time}{reset} " # time
        f"[ {status_color}{bold}{status_text}{reset} ]" # status
    )

    # add additional fields
    if guild:
        log_entry += f" [ {guild_color}{bold}GUILD {guild}{reset} ]"
    if function:
        log_entry += f" [ {function_color}{bold}{function.upper()}{reset} ]"
    log_entry += f" {message}"


    # ensure log directory exists and write to file
    os.makedirs("data", exist_ok=True)
    log_path = os.path.join("data", "log.log")
    
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            content = f"[ {today} {current_time} ] [ {status_text} ]"

            if guild:
                content += f" [ GUILD {guild} ]"
            if function:
                content += f" [ {function.upper()} ]"

            content += f" {message}\n"

            f.write(content)
            
    except Exception as e:
        print(f"Failed to write to log file: {e}")

    # show in console
    print(log_entry)


event_usage = Counter()
def event(event_name: str): # custom event handler (this is separate from events, so its a different counter)
    event_usage[event_name] += 1
    logmsg("DEBUG", f"Event tracked: {event_name}", 
           function="event")