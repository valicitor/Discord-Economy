import discord
from discord import Interaction

from application import (
    WorkCommandResponse
)
from application.helpers.helpers import Helpers

class DiscordWorkEmbed:

    @staticmethod
    async def work_embed(interaction: discord.Interaction, response: WorkCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
        color = discord.Color.green() if response.action_success else discord.Color.red()

        business_name = response.business.name if response.business and response.business.name else "Unknown Business"
        action_name = response.action.name if response.action and response.action.name else "Unknown Action"
        business_message = response.action.success_message if response.action_success else response.action.failure_message
        balance_message = f"You were paid {currency}{response.wage}!" if response.action_success else f"You were fined {currency}{response.fine}!"

        embed=discord.Embed(
            description=f"### {response.player.player.name}\n**{business_name} - {action_name}**\n{business_message}\n{balance_message}",
            color=color
        )
        
        embed.set_footer(text=f"Cooldown: {Helpers.format_countdown(response.action.cooldown_seconds)}")

        return embed
    
    @staticmethod
    async def crime_embed(interaction: discord.Interaction, response: WorkCommandResponse):
        currency = await response.server_config.get_default_currency_symbol()
        color = discord.Color.green() if response.action_success else discord.Color.red()

        business_name = response.business.name if response.business and response.business.name else "Unknown Business"
        action_name = response.action.name if response.action and response.action.name else "Unknown Action"
        business_message = response.action.success_message if response.action_success else response.action.failure_message
        balance_message = f"You were paid {currency}{response.wage}!" if response.action_success else f"You were fined {currency}{response.fine}!"

        embed=discord.Embed(
            description=f"### {response.player.player.name}\n**{business_name} - {action_name}**\n{business_message}\n{balance_message}",
            color=color
        )
        
        embed.set_footer(text=f"Cooldown: {Helpers.format_countdown(response.action.cooldown_seconds)}")

        return embed