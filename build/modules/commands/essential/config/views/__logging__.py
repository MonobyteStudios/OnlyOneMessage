import discord
from essential.logging import logmsg
from essential.data import encrypt, decrypt
from ..__configutils__ import refreshview
import aiohttp

class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, bot, channel):
        self.bot = bot
        self.serverdata = bot.serverdata

        super().__init__(
            placeholder="Select a logging channel...",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            default_values=[channel] if channel else None
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0] if self.values else None
        selectedchannel = interaction.guild.get_channel(selected.id) if selected else None
        data = self.serverdata.find_one({"_id": interaction.guild.id}) or {}

        async with aiohttp.ClientSession() as session:
            webhookurl = decrypt(data.get("config", {}).get("loggingchannel", None))
            webhook = discord.Webhook.from_url(webhookurl, session=session) if webhookurl else None

        async def deletewebhook(webhook, reason):
            async with aiohttp.ClientSession() as session:
                wh = discord.Webhook.from_url(webhook, session=session)
                try:
                    await wh.delete(reason=reason) 
                    logmsg("DEBUG", f"Successfully deleted webhook {webhook}", # the webhook got deleted so its safe to show
                        guild=str(interaction.guild.id), function="channelselect_callback")
                    
                except:
                    pass
        
        # make sure the bot can manage webhooks
        if selectedchannel and not selectedchannel.permissions_for(interaction.guild.me).manage_webhooks:
            await interaction.response.send_message(
                "❌ I need the `Manage Webhooks` permission to set up logging.",
                ephemeral=True
            )
            return
        


        if not selectedchannel: # if a channel is no longer selected
            if webhook:
                await deletewebhook(webhookurl, "OOM logging has been disabled")
            webhookurl = None


        elif not webhookurl: # if there's no existing webhook
            new_webhook = await selectedchannel.create_webhook(
                name="OnlyOneMessage", 
                avatar=await self.bot.user.display_avatar.read()
            )
            webhookurl = new_webhook.url

            logmsg("DEBUG", f"Successfully created new webhook for channel {selectedchannel.id}",
                    guild=str(interaction.guild.id), function="channelselect_callback")
            

        elif selectedchannel.id != webhook.channel_id: # if a new channel is selected
            await deletewebhook(webhookurl, "OOM logging has been changed")

            new_webhook = await selectedchannel.create_webhook(
                name="OnlyOneMessage", 
                avatar=await self.bot.user.display_avatar.read()
            )
            webhookurl = new_webhook.url

            logmsg("DEBUG", f"Successfully created new webhook for channel {selectedchannel.id}",
                    guild=str(interaction.guild.id), function="channelselect_callback")



        logmsg("DEBUG", f"Setting logging to channel {selectedchannel.id if selectedchannel else 'None'} with webhook",
            guild=str(interaction.guild.id), function="channelselect_callback")
        
        
        self.serverdata.update_one(
            {"_id": interaction.guild.id},
            {"$set": {
                "config.loggingchannel": encrypt(webhookurl) if webhookurl else None,
                "config.loggingchannelid": selectedchannel.id if selectedchannel else 0
            }},
            upsert=True
        )
        await self.bot.logconfig(self.bot, interaction.user, "Logging", ('Logging disabled' if selectedchannel is None else f'<#{selectedchannel.id}> (ID `{selectedchannel.id}`)'))

        view = await refreshview(interaction.guild, self.bot)
        await interaction.response.edit_message(view=view)



class CategorySelection(discord.ui.Select):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.serverdata = bot.serverdata

        serverdata = self.serverdata.find_one({"_id": self.guild.id})
        selected = serverdata.get("config", {}).get("loggingcategories", [])

        options = [
            discord.SelectOption(label="Slowmodes Applied", value="blacklist", emoji="⛈️", default="blacklist" in selected),
            discord.SelectOption(label="Slowmodes Removed", value="unblacklist", emoji="🔓", default="unblacklist" in selected),
            discord.SelectOption(label="Message Deletions", value="deletions", emoji="🗑️", default="deletions" in selected),
            discord.SelectOption(label="Configuration Changes", value="config", emoji="⚙️", default="config" in selected),
        ]

        super().__init__(
            placeholder="Select categories to log...",
            min_values=1,  # require at least one selection
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        def format_category_list(categories):
            if not categories:
                return "None"
            return ", ".join(categories)

        await self.bot.logconfig(self.bot, interaction.user, "Logging Categories", f"`{format_category_list(self.values)}`")
        logmsg("DEBUG", f"Logging categories selected: {self.values}",
                guild=str(interaction.guild.id), function="CategorySelection_callback")

        self.serverdata.update_one(
            {"_id": interaction.guild.id},
            {"$set": {"config.loggingcategories": self.values}},
            upsert=True
        )

        await interaction.response.send_message( # discord will reply to the message
            f"✅ Successfully applied category changes!",
            ephemeral=True
        )




async def settingOptions(guild: discord.Guild, bot):
    container = discord.ui.Container()

    container.add_item(
        discord.ui.TextDisplay(
            "## 📰 Logging \n"
            "*Manage what events are logged in your server."
            " Select a channel to enable logging, and select categories to log, if needed.*"
        )
    )

    container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

    serverdata = bot.serverdata.find_one({"_id": guild.id})
    logging = serverdata.get("config", {}).get("loggingchannelid", None)
    loggingchannel = guild.get_channel(logging)

    container.add_item(
        discord.ui.TextDisplay(
            f"Set channel: {'`None`' if not loggingchannel else f'<#{loggingchannel.id}> `(ID {loggingchannel.id})`'}\n"
        )
    )


    container.add_item(
        discord.ui.ActionRow(
            CategorySelection(bot, guild)
        )
    )
    container.add_item(
        discord.ui.ActionRow(
            ChannelSelect(bot, loggingchannel)
        )
    )
    
    return container.children
