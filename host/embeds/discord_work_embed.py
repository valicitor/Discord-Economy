import discord
from discord import Interaction

from application import get_default_currency
from application import (
    WorkCommandResponse
)
from application.helpers.get_cooldown import get_countdown

class DiscordWorkEmbed:

    @staticmethod
    async def work_embed(interaction: discord.Interaction, response: WorkCommandResponse):
        currency = await get_default_currency(response.server_config)
        color = discord.Color.green() if response.action_success else discord.Color.red()

        business_name = response.business.name if response.business and response.business.name else "Unknown Business"
        action_name = response.action.name if response.action and response.action.name else "Unknown Action"
        business_message = response.action.success_message if response.action_success else response.action.failure_message
        balance_message = f"You were paid {currency}{response.wage}!" if response.action_success else f"You were fined {currency}{response.fine}!"

        embed=discord.Embed(
            description=f"**{business_name} - {action_name}**\n{business_message}\n{balance_message}",
            color=color
        )
        
        embed.set_author(name=f"{response.player.player.username}", icon_url=f"{response.player.player.avatar}")
        embed.set_footer(text=f"Cooldown: {get_countdown(response.action.cooldown_seconds)}")

        return embed