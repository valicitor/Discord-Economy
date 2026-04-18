import discord
from discord import Interaction

from application import get_default_currency
from application import (
    GetBalanceQueryResponse, 
    PayCommandResponse,
    WithdrawCommandResponse, 
    DepositCommandResponse,
    GetLeaderboardQueryResponse
)

class DiscordBalanceEmbed:

    @staticmethod
    async def get_balance_embed(interaction: Interaction, response: GetBalanceQueryResponse):
        currency = await get_default_currency(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"Leaderboard Rank: **#{response.player.player.rank}** \n Faction: **{response.player.faction.name if response.player.faction else 'None'}**",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        embed.set_author(name=f"{response.player.player.username}", icon_url=f"{response.player.player.avatar}")
        for balance in response.player.balances:
            embed.add_field(name=f"Balance", value=f"{currency}{balance.balance}", inline=True)
        for bank_account in response.player.bank_accounts:  
            embed.add_field(name="Bank", value=f"{currency}{bank_account.balance}", inline=True)
        return embed
    
    @staticmethod
    async def withdraw_embed(interaction: Interaction, response: WithdrawCommandResponse):
        currency = await get_default_currency(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"✅ Withdrew {currency}{response.amount} from your bank!",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        embed.set_author(name=f"{response.player.player.username}", icon_url=f"{response.player.player.avatar}")
        return embed

    @staticmethod
    async def deposit_embed(interaction: Interaction, response: DepositCommandResponse):
        currency = await get_default_currency(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"✅ Deposited {currency}{response.amount} into your bank!",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        embed.set_author(name=f"{response.player.player.username}", icon_url=f"{response.player.player.avatar}")
        return embed

    @staticmethod
    async def pay_balance_embed(interaction: discord.Interaction, target: discord.User, response: PayCommandResponse):
        currency = await get_default_currency(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None
      
        embed = discord.Embed(
            title=f"💳 Bank Account",
            description=f"{interaction.user.mention}, you have paid {target.mention} **{currency}{response.amount}**.",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        return embed
    
    @staticmethod
    async def get_leaderboard_embed(interaction: discord.Interaction, response: GetLeaderboardQueryResponse):
        currency = await get_default_currency(response.server_config)

        description=f"View the leaderboard here:\n"
        for player_profile in response.players:
            money = player_profile.balances.total_balance() if response.sort_by == "Cash" else player_profile.bank_accounts.total_bank_balance() if response.sort_by == "Bank" else player_profile.balances.total_balance() + player_profile.bank_accounts.total_bank_balance()
            description+=f"\n**{player_profile.player.rank}.** `{player_profile.player.username}` • {currency}{money}"
                
        embed=discord.Embed(
            title=f"🏆 Leaderboard [{response.sort_by}]", 
            description=description, 
            color=discord.Color.gold()
        )

        embed.set_footer(text=f"Page {response.page}/{response.max_pages}")

        return embed