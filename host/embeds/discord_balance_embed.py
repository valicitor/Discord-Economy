import discord
from discord import Interaction

from application.services.helpers import Helpers
from application import (
    DiscordGuild,
    GetBalanceQueryResponse,
    PayCommandResponse,
    WithdrawCommandResponse,
    DepositCommandResponse,
    GetLeaderboardQueryResponse,
    GetLeaderboardQuery, GetLeaderboardQueryRequest,
)


class DiscordBalanceEmbed:

    class GetBalanceLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetBalanceQueryResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetBalanceQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            hex_color = self.response.player.faction.color if self.response.player.faction and self.response.player.faction.color else None

            items = []
            for b in self.response.player.balances:
                items.append(discord.ui.TextDisplay(content=f"**Balance:** {currency}{Helpers.format_cash_amount(b.balance)}"))
            for b in self.response.player.bank_accounts:
                items.append(discord.ui.TextDisplay(content=f"**Bank:** {currency}{Helpers.format_cash_amount(b.balance)}"))

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### {self.response.player.player.name}"),
                    discord.ui.Separator(),
                    *items,
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue(),
                    spoiler=False
                )
            )


    class WithdrawLayoutView(discord.ui.LayoutView):
        def __init__(self, response: WithdrawCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: WithdrawCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            hex_color = self.response.player.faction.color if self.response.player.faction and self.response.player.faction.color else None
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content=f"✅ Withdrew {currency}{Helpers.format_cash_amount(self.response.amount)} from your bank!"),
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue(),
                    spoiler=False
                )
            )


    class DepositLayoutView(discord.ui.LayoutView):
        def __init__(self, response: DepositCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: DepositCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            hex_color = self.response.player.faction.color if self.response.player.faction and self.response.player.faction.color else None
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content=f"✅ Deposited {currency}{Helpers.format_cash_amount(self.response.amount)} into your bank!"),
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue(),
                    spoiler=False
                )
            )


    class PayLayoutView(discord.ui.LayoutView):
        def __init__(self, response: PayCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: PayCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            hex_color = self.response.player.faction.color if self.response.player.faction and self.response.player.faction.color else None
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💳 Payment Sent"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(
                        content=f"**{self.response.player.player.name}** paid **{self.response.target_player.player.name}** "
                                f"{currency}{Helpers.format_cash_amount(self.response.amount)}."
                    ),
                    accent_color=discord.Colour.from_str(hex_color) if hex_color else discord.Color.blue(),
                    spoiler=False
                )
            )


    class LeaderboardLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetLeaderboardQueryResponse | None = None, guild: DiscordGuild | None = None):
            self.response = response
            self.guild = guild
            super().__init__()

        @classmethod
        async def create(cls, response: GetLeaderboardQueryResponse, guild: DiscordGuild):
            view = cls(response, guild)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            lines = []
            for p in self.response.players:
                if self.response.sort_by == "Cash":
                    money = p.balances.total_balance()
                elif self.response.sort_by == "Bank":
                    money = p.bank_accounts.total_bank_balance()
                else:
                    money = p.balances.total_balance() + p.bank_accounts.total_bank_balance()
                lines.append(f"**{p.player.rank}.** `{p.player.name}` • {currency}{Helpers.format_cash_amount(money)}")

            nav_items = []
            if self.response.page > 1:
                prev_btn = discord.ui.Button(label="◀ Prev", style=discord.ButtonStyle.secondary)
                async def prev_callback(interaction: discord.Interaction, view=self):
                    try:
                        req = GetLeaderboardQueryRequest(guild=view.guild, page=view.response.page - 1, sort_by=view.response.sort_by, limit=10)
                        resp = await GetLeaderboardQuery(req).execute()
                        new_view = await DiscordBalanceEmbed.LeaderboardLayoutView.create(resp, view.guild)
                        await interaction.response.edit_message(view=new_view)
                    except Exception as e:
                        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
                prev_btn.callback = prev_callback
                nav_items.append(discord.ui.Section(discord.ui.TextDisplay(content="Previous page"), accessory=prev_btn))

            if self.response.page < self.response.max_pages:
                next_btn = discord.ui.Button(label="Next ▶", style=discord.ButtonStyle.secondary)
                async def next_callback(interaction: discord.Interaction, view=self):
                    try:
                        req = GetLeaderboardQueryRequest(guild=view.guild, page=view.response.page + 1, sort_by=view.response.sort_by, limit=10)
                        resp = await GetLeaderboardQuery(req).execute()
                        new_view = await DiscordBalanceEmbed.LeaderboardLayoutView.create(resp, view.guild)
                        await interaction.response.edit_message(view=new_view)
                    except Exception as e:
                        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
                next_btn.callback = next_callback
                nav_items.append(discord.ui.Section(discord.ui.TextDisplay(content="Next page"), accessory=next_btn))

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content=f"## Leaderboard [{self.response.sort_by}]"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content="\n".join(lines) if lines else "No players found."),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"-# Page {self.response.page}/{self.response.max_pages}"),
                    *nav_items,
                    accent_color=discord.Color.gold(),
                    spoiler=False
                )
            )


    @staticmethod
    async def get_balance_view(interaction: Interaction, response: GetBalanceQueryResponse):
        return await DiscordBalanceEmbed.GetBalanceLayoutView.create(response)

    @staticmethod
    async def get_withdraw_view(interaction: Interaction, response: WithdrawCommandResponse):
        return await DiscordBalanceEmbed.WithdrawLayoutView.create(response)

    @staticmethod
    async def get_deposit_view(interaction: Interaction, response: DepositCommandResponse):
        return await DiscordBalanceEmbed.DepositLayoutView.create(response)

    @staticmethod
    async def get_pay_view(interaction: Interaction, response: PayCommandResponse):
        return await DiscordBalanceEmbed.PayLayoutView.create(response)

    @staticmethod
    async def get_leaderboard_view(interaction: Interaction, response: GetLeaderboardQueryResponse, guild: DiscordGuild):
        return await DiscordBalanceEmbed.LeaderboardLayoutView.create(response, guild)
