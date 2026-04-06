import discord
from discord import Interaction

from application import get_default_currenncy
from application import (
    GetBalanceQueryResponse, 
    PayCommandResponse,
    WithdrawCommandResponse, 
    DepositCommandResponse,
    GetLeaderboardQueryResponse,
    GetEquipmentQueryResponse,
    GetRaceQueryResponse
)

class DiscordBalanceEmbed:

    @staticmethod
    def get_balance_embed(interaction: Interaction, response: GetBalanceQueryResponse):
        currency = get_default_currenncy(response.server_config)
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
    def withdraw_embed(interaction: Interaction, response: WithdrawCommandResponse):
        currency = get_default_currenncy(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"✅ Withdrew {currency}{response.amount} from your bank!",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        embed.set_author(name=f"{response.player.player.username}", icon_url=f"{response.player.player.avatar}")
        return embed

    @staticmethod
    def deposit_embed(interaction: Interaction, response: DepositCommandResponse):
        currency = get_default_currenncy(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None

        embed=discord.Embed(
            description=f"✅ Deposited {currency}{response.amount} into your bank!",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        
        embed.set_author(name=f"{response.player.player.username}", icon_url=f"{response.player.player.avatar}")
        return embed

    @staticmethod
    def pay_balance_embed(interaction: discord.Interaction, target: discord.User, response: PayCommandResponse):
        currency = get_default_currenncy(response.server_config)
        hex_color = response.player.faction.color if response.player.faction and response.player.faction.color else None
      
        embed = discord.Embed(
            title=f"💳 Bank Account",
            description=f"{interaction.user.mention}, you have paid {target.mention} **{currency}{response.amount}**.",
            color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue()
        )
        return embed
    
    @staticmethod
    def get_leaderboard_embed(interaction: discord.Interaction, response: GetLeaderboardQueryResponse):
        currency = get_default_currenncy(response.server_config)

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
    
    @staticmethod
    def get_equipment_stat_block_embed(interaction: discord.Interaction, response: GetEquipmentQueryResponse):
        embed = discord.Embed(
            title=f"{response.equipment.name}", 
            description=response.equipment.description, 
            color=discord.Color.blue()
        )

        header_row = []
        seperator_row = []
        stat_rows = []
        for stat in response.stats:
            char_length = len(str(stat.stat_key))
            header_row.append(f"{stat.stat_key:^{char_length}}")
            stat_rows.append(f"{stat.stat_value:^{char_length}}")
            seperator_row.append("-" * char_length)
            
        # Combine everything into a code block
        stat_block = "```\n" + " | ".join(header_row) + "\n" + "-+-".join(seperator_row) + "\n" + " | ".join(stat_rows) + "\n```"

        embed.add_field(name="", value=stat_block, inline=False)

        for keyword in response.keywords:
            embed.add_field(name=keyword.name, value=keyword.description, inline=False)

        return embed
    
    @staticmethod
    def get_race_stat_block_embed(interaction: discord.Interaction, response: GetRaceQueryResponse):
        embed = discord.Embed(
            title=f"{response.race.name}", 
            description=response.race.description, 
            color=discord.Color.blue()
        )

        categories = {
            "Stats": ["WS", "BS", "T", "W"],
            "Unarmed": ["Attacks", "S", "AP", "D", "Range"],
            "Unarmored": ["Sv"]
        }
        for category, keys in categories.items():
            header_row = []
            seperator_row = []
            stat_rows = []
            for stat in response.stats:
                if stat.stat_key in keys:
                    char_length = len(str(stat.stat_key)) +1
                    header_row.append(f"{stat.stat_key:^{char_length}}")
                    stat_rows.append(f"{stat.stat_value:^{char_length}}")
                    seperator_row.append("-" * char_length)
                
            # Combine everything into a code block
            stat_block = "```\n" + " | ".join(header_row) + "\n" + "-+-".join(seperator_row) + "\n" + " | ".join(stat_rows) + "\n```"

            embed.add_field(name=category, value=stat_block, inline=False)

        for keyword in response.keywords:
            embed.add_field(name=keyword.name, value=keyword.description, inline=False)

        return embed

    # @staticmethod
    # def work_embed(interaction: discord.Interaction, response: WorkCommandResponse):
    #     currency = get_default_currenncy(response.server_config)

    #     embed=discord.Embed(
    #         description=f"💼 You worked and earned {currency}{response.amount}!",
    #         color=discord.Color.green()
    #     )
        
    #     embed.set_author(name=f"{response.user.username}", icon_url=f"{response.user.avatar}")
    #     return embed