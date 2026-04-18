import discord
from discord import Interaction

from application import (
    GetEquipmentQueryResponse,
    GetRaceQueryResponse
)

class DiscordUnitsEmbed:    

    @staticmethod
    async def get_equipment_stat_block_embed(interaction: discord.Interaction, response: GetEquipmentQueryResponse):
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
    async def get_race_stat_block_embed(interaction: discord.Interaction, response: GetRaceQueryResponse):
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