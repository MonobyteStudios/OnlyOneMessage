import discord
from essential.logging import logmsg
from ..command import refreshview

def format_duration(seconds):
    try:
        seconds = int(seconds)

    except ValueError:
        raise ValueError(f"Invalid duration value: {seconds}")

    if seconds == 0:
        return "Forever"

    units = [
        ('day', 86400),
        ('hour', 3600),
    ]

    for name, duration in units:
        if seconds % duration == 0:
            count = seconds // duration
            return f"{count} {name}" + ("s" if count != 1 else "")

    return f"{seconds} seconds"


class CooldownSelect(discord.ui.Select):
    def __init__(self, bot, channel):
        self.bot = bot
        self.serverdata = bot.serverdata
        self.channel = channel

        options = [
            discord.SelectOption(label="Forever", value=0, description="Disable cooldown"),
            discord.SelectOption(label="12 Hours", value=43200),
            discord.SelectOption(label="1 Day", value=86400),
            discord.SelectOption(label="3 Days", value=259200),
            discord.SelectOption(label="7 Days", value=604800),
            discord.SelectOption(label="14 Days", value=1209600),
            discord.SelectOption(label="1 Month", value=2592000),
        ]
        super().__init__(
            placeholder="Select a duration...",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_value = int(self.values[0])
        logmsg("DEBUG", f"Setting channel {self.channel.id} cooldown to {selected_value} ({format_duration(selected_value)})", 
               guild=str(interaction.guild.id), function="cooldownselect_callback")

        self.serverdata.update_one(
            {"_id": interaction.guild.id},  
            {"$set": {f"channels.{str(self.channel.id)}.cooldown": selected_value}}
        )
        
        view = await refreshview(interaction.guild, self.bot, self.channel)
        await interaction.response.edit_message(view=view)

        await self.bot.logconfig(self.bot, interaction.user, f"{self.channel.mention}'s Cooldown", f"`{format_duration(selected_value)}`")
        await send_channel_message(interaction, self.bot, self.channel)



async def settingOptions(guild: discord.Guild, bot, channel: discord.TextChannel):
    serverdata = bot.serverdata.find_one({"_id": guild.id})
    channeldata = serverdata.get("channels", {}).get(str(channel.id), {})

    recovery = channeldata.get("recovery", False)
    cooldown = channeldata.get("cooldown", 0)
    reactions = channeldata.get("reactions", False)

    container = discord.ui.Container()

    # Cooldown Duration
    container.add_item(
        discord.ui.TextDisplay(
            "### 🕒 Cooldown Duration\n"
            "Configure how long members are in slowmode after sending a message in this channel. "
        )
    )

    container.add_item(
        discord.ui.TextDisplay(f"Status: `{format_duration(cooldown)}`")
    )
    container.add_item(
        discord.ui.ActionRow(
            CooldownSelect(bot, channel)
        )
    )


    container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))


    # Message Recovery
    button = discord.ui.Button(
        emoji="🛠️",
        style=discord.ButtonStyle.secondary,
    )
    async def toggledeletion_callback(interaction: discord.Interaction):
        logmsg("DEBUG", f"Setting channel {channel.id} message recovery from {recovery} to {not recovery}",
                guild=str(interaction.guild.id), function="toggledeletion_callback")
        
        bot.serverdata.update_one(
            {"_id": interaction.guild.id},
            {"$set": {f"channels.{str(channel.id)}.recovery": not recovery}}
        )

        view = await refreshview(interaction.guild, bot, channel)
        await interaction.response.edit_message(view=view)

        await bot.logconfig(bot, interaction.user, f"{channel.mention}'s Message Recovery", f"`{'✅ Enabled' if not recovery else '❌ Disabled'}`")

    button.callback = toggledeletion_callback


    container.add_item(
        discord.ui.Section(
            discord.ui.TextDisplay(
                "### 🗑️ Message Recovery\n"
                "Manage whether members can chat again by deleting their message. "
                "Their slowmode role will automatically be removed when they delete their message in the set channel.\n\n"
                f"Status: `{'✅ Enabled' if recovery else '❌ Disabled'}`"
            ),
            accessory=button
        )
    )


    container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))


    # Reactions
    button = discord.ui.Button(
        emoji="🛠️",
        style=discord.ButtonStyle.secondary,
    )
    async def togglereactions_callback(interaction: discord.Interaction):
        logmsg("DEBUG", f"Setting channel {channel.id} reactions from {reactions} to {not reactions}",
                guild=str(interaction.guild.id), function="togglereactions_callback")
        
        bot.serverdata.update_one(
            {"_id": interaction.guild.id},
            {"$set": {f"channels.{str(channel.id)}.reactions": not reactions}}
        )

        view = await refreshview(interaction.guild, bot, channel)
        await interaction.response.edit_message(view=view)

        await bot.logconfig(bot, interaction.user, f"{channel.mention}'s Reactions", f"`{'✅ Enabled' if not reactions else '❌ Disabled'}`")

    button.callback = togglereactions_callback

    container.add_item(
        discord.ui.Section(
            discord.ui.TextDisplay(
                "### 🎭 Reactions\n"
                "Toggle whether reactions are added to member messages in this channel. These indicate slowmode status.\n\n"

                f"Status: `{'✅ Enabled' if reactions else '❌ Disabled'}`"
            ), accessory=button
        )
    )

    return container.children



async def send_channel_message(interaction: discord.Interaction, bot, channel):
    if channel: # make sure channel exists before trying to send message
        serverdata = bot.serverdata.find_one({"_id": interaction.guild.id}) or {}
        channeldata = serverdata.get("channels", {}).get(str(channel.id), {})

        try:
            await channel.send(
                f"-# This channel's cooldown has been set to `{format_duration(channeldata.get('cooldown', 0))}`."
            )

        except discord.Forbidden:
            logmsg("WARNING", f"Failed to send message in channel {channel.id}: Forbidden", 
                guild=str(interaction.guild.id), function="send_channel_message")