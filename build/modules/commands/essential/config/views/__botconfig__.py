import discord
from essential.logging import logmsg, event
from essential.data import create_guild_data
from ..__configutils__ import refreshview


async def settingOptions(guild: discord.Guild, bot):
    serverdata = bot.serverdata.find_one({"_id": guild.id})
    functions = serverdata.get("config", {}).get("functions", True)

    container = discord.ui.Container()

    container.add_item(
        discord.ui.TextDisplay(
            "## ⚙️ Bot Configuration \n"
            "*Manage basic settings for OnlyOneMessage.*"
        )
    )

    container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

    # Disable Functions
    button = discord.ui.Button(
        emoji="🛠️",
        style=discord.ButtonStyle.secondary
    )
    async def togglefunctionality_callback(interaction: discord.Interaction):
        logmsg("DEBUG", f"Setting bot functionality from {functions} to {not functions}",
                guild=str(interaction.guild.id), function="togglefunctionality_callback")
        
        bot.serverdata.update_one(
            {"_id": interaction.guild.id},
            {"$set": {"config.functions": not functions}}
        )

        view = await refreshview(interaction.guild, bot)
        await interaction.response.edit_message(view=view)
        
        await bot.logconfig(bot, interaction.user, "Bot Functionalty", f"`{'✅ Functions Enabled' if not functions else '❌ Functions Disabled'}`")

    button.callback = togglefunctionality_callback


    container.add_item(
        discord.ui.Section(
            discord.ui.TextDisplay(
                "### ❌ Disable Functions\n"
                "Temporarily disable OnlyOneMessage and its functionality. Once disabled, OnlyOneMessage will no longer handle cooldowns.\n\n"
                f"Status: `{'✅ Functions Enabled' if functions else '❌ Functions Disabled'}`"
            ),
            accessory=button
        )
    )
    return container.children
