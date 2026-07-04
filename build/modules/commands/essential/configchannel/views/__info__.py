import discord

async def settingOptions(guild: discord.Guild, bot, channel: discord.TextChannel):
    container = discord.ui.Container()

    container.add_item(
        discord.ui.TextDisplay(
            f"## 💻 {channel.mention} \n"
            "*Configure settings for this channel.*"
        )
    )

    return container.children
