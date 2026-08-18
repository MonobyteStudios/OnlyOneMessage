import discord
from discord import app_commands
from collections import defaultdict, deque
import time

from essential.logging import logmsg
from essential.metadata import ADMIN_IDS

def requireguild(interaction: discord.Interaction, function: str):
    if interaction.guild is None:
        logmsg("DEBUG", "Raising NoPrivateMessage error due to command being in DM's", function=function)
        raise app_commands.NoPrivateMessage("This command cannot be used in DMs.")
    return True


def user_check(**permissions):
    def predicate(interaction: discord.Interaction):
        requireguild(interaction, function="user_check")

        member_permissions = interaction.user.guild_permissions
        missing = [perm for perm, value in permissions.items() if getattr(member_permissions, perm, False) != value]

        if missing:
            logmsg("DEBUG", "User does not have required role permissions. Raising error.",
                   guild=str(interaction.guild.id), function="user_check")
            raise app_commands.MissingPermissions(missing)
        
        return True
    return app_commands.check(predicate)


def bot_check(**permissions):
    def predicate(interaction: discord.Interaction):
        requireguild(interaction, function="bot_check")

        bot_member = interaction.guild.me

        bot_perms = bot_member.guild_permissions
        missing = [perm for perm, value in permissions.items() if getattr(bot_perms, perm, False) != value]

        if missing:
            logmsg("DEBUG", "Bot does not have required permissions. Raising error.",
                   guild=str(interaction.guild.id), function="bot_check")
            raise app_commands.BotMissingPermissions(missing)
        
        return True
    return app_commands.check(predicate)


def is_admin(user_id: int):
    return user_id in ADMIN_IDS

def guild_only():
    def predicate(interaction: discord.Interaction):
        requireguild(interaction, function="guild_only")
        return True
    
    return app_commands.check(predicate)


flood_tracker = defaultdict(lambda: deque(maxlen=100))
def is_guild_flooding(guild_id: int, max_events: int = 30, window: float = 5.0):
    now = time.time()
    
    events = flood_tracker[guild_id]
    events.append(now)

    recent_events = sum(1 for t in events if now - t <= window)
    return recent_events >= max_events