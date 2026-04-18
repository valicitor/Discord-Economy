import discord
from discord import app_commands
from discord.ext import commands

from application import DiscordGuild, DiscordUser
from application import (
    WorkCommand, WorkCommandRequest
)
from host.embeds.discord_work_embed import DiscordWorkEmbed

class WorkCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- /work ---
    @app_commands.command(name="work", description="Work to earn money.")
    @app_commands.guild_only()
    async def user_work(self, interaction: discord.Interaction):
        try:
            guild = DiscordGuild(
                guild_id=interaction.guild_id, 
                name=interaction.guild.name
            )
            user = DiscordUser(
                user_id=interaction.user.id,
                name=interaction.user.name,
                display_avatar=str(interaction.user.display_avatar)
            )
        
            request=WorkCommandRequest(
                guild=guild, 
                user=user
            )

            response = await WorkCommand(request).execute()

            embed = await DiscordWorkEmbed.work_embed(interaction, response)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WorkCog(bot))
