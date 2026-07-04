import discord
from discord.ext import commands
from discord import app_commands
from essential.metadata import DEV_GUILDS
from essential.checks import is_admin
from essential.logging import logmsg

class Guilds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(*DEV_GUILDS)
    @app_commands.command(name="guilds", description="[DEV] List all guilds the bot is in")
    async def guilds(self, interaction: discord.Interaction):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
        logmsg("DEBUG", "/guilds executed", 
               function="guilds", guild=str(interaction.guild.id))
        

        guilds = list(self.bot.guilds)
        maxamount = 10

        pages = [guilds[i:i + maxamount] for i in range(0, len(guilds), maxamount)]
        total_pages = len(pages)
        if total_pages == 0:
            return


        current_page = 0
        def renderview(page_index: int):
            view = discord.ui.LayoutView(timeout=None)
            container = discord.ui.Container()

            container.add_item(
                discord.ui.TextDisplay(
                    f"### 💻 OnlyOneMessage Guilds (Page {page_index+1}/{total_pages})"
                )
            )


            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))


            # guild display
            guild_text = ""
            for guild in pages[page_index]:
                guild_text += (
                    f"> **{guild.name}** (`{guild.id}`)\n"

                    f"👥 `{guild.member_count:,}` Members\n"
                    f"👑 Owner: `{guild.owner}` (`{guild.owner_id}`)\n"
                    f"📆 Creation Date: `{guild.created_at.strftime('%Y-%m-%d')}`\n\n"
                )

            container.add_item(
                discord.ui.TextDisplay(guild_text.strip())
            )


            container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))


            # pagination
            last = discord.ui.Button(
                emoji="⬅️",
                style=discord.ButtonStyle.secondary,
                disabled=(page_index == 0)
            )
            async def last_callback(interaction: discord.Interaction):
                if page_index > 0:
                    new_page = page_index - 1
                    await interaction.response.edit_message(view=renderview(new_page))
                    logmsg("DEBUG", f"Paginated to page {new_page + 1}", 
                           guild=str(interaction.guild.id), function="guilds")

            last.callback = last_callback


            next = discord.ui.Button(
                emoji="➡️",
                style=discord.ButtonStyle.secondary,
                disabled=(page_index == total_pages - 1)
            )
            async def next_callback(interaction: discord.Interaction):
                if page_index < total_pages - 1:
                    new_page = page_index + 1
                    await interaction.response.edit_message(view=renderview(new_page))
                    logmsg("DEBUG", f"Paginated to page {new_page + 1}", 
                           guild=str(interaction.guild.id), function="guilds")

            next.callback = next_callback


            container.add_item(
                discord.ui.ActionRow(last, next)
            )

            view.add_item(container)
            return view
        

        view = renderview(current_page)
        view.current_page = current_page
        await interaction.response.send_message(view=view, ephemeral=True)
        logmsg("DEBUG", f"Sent guild list with {len(guilds)} guilds in {total_pages} page(s)", 
               guild=str(interaction.guild.id), function="guilds")


async def setup(bot):
    await bot.add_cog(Guilds(bot))
