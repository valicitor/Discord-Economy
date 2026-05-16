import discord
from discord import Interaction

from application.services.helpers import Helpers
from application import (
    BuyStockCommandResponse,
    GetStocksQueryResponse,
    PayDividendsCommandResponse,
    TakeLoanCommandResponse,
    RepayLoanCommandResponse,
    ExchangeCommandResponse,
)


class DiscordEconomyEmbed:

    class StocksLayoutView(discord.ui.LayoutView):
        def __init__(self, response: GetStocksQueryResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: GetStocksQueryResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            if not self.response.holdings:
                self.add_item(
                    discord.ui.Container(
                        discord.ui.TextDisplay(content="## 📈 Your Stock Portfolio"),
                        discord.ui.Separator(),
                        discord.ui.TextDisplay(content="You don't own any stocks yet. Use `/buy-stock` to invest."),
                        accent_color=discord.Color.green(),
                        spoiler=False
                    )
                )
                return

            holding_items = []
            for player_stock, business_stock, business in self.response.holdings:
                value = player_stock.quantity * business_stock.current_price
                if holding_items:
                    holding_items.append(discord.ui.Separator())
                holding_items.append(discord.ui.TextDisplay(content=f"**{business.name}**"))
                holding_items.append(discord.ui.TextDisplay(
                    content=f"Shares: **{player_stock.quantity}** | "
                            f"Price: **{currency}{business_stock.current_price}** | "
                            f"Value: **{currency}{Helpers.format_cash_amount(value)}**"
                ))

            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 📈 Your Stock Portfolio"),
                    discord.ui.Separator(),
                    *holding_items,
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class BuyStockLayoutView(discord.ui.LayoutView):
        def __init__(self, response: BuyStockCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: BuyStockCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 📈 Stock Purchased"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Shares Bought:** {self.response.quantity}"),
                    discord.ui.TextDisplay(content=f"**Price / Share:** {currency}{self.response.business_stock.current_price}"),
                    discord.ui.TextDisplay(content=f"**Total Cost:** {currency}{Helpers.format_cash_amount(self.response.total_cost)}"),
                    accent_color=discord.Color.green(),
                    spoiler=False
                )
            )


    class PayDividendsLayoutView(discord.ui.LayoutView):
        def __init__(self, response: PayDividendsCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: PayDividendsCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💰 Dividends Paid"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Business:** {self.response.business_name}"),
                    discord.ui.TextDisplay(content=f"**Recipients:** {self.response.recipients}"),
                    discord.ui.TextDisplay(content=f"**Total Paid Out:** {currency}{Helpers.format_cash_amount(self.response.total_paid)}"),
                    accent_color=discord.Color.gold(),
                    spoiler=False
                )
            )


    class TakeLoanLayoutView(discord.ui.LayoutView):
        def __init__(self, response: TakeLoanCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: TakeLoanCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 🏦 Loan Approved"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Amount Received:** {currency}{Helpers.format_cash_amount(self.response.loan.principal)}"),
                    discord.ui.TextDisplay(content=f"**Total to Repay:** {currency}{Helpers.format_cash_amount(self.response.loan.balance_remaining)}"),
                    discord.ui.TextDisplay(content=f"**Interest Rate:** {self.response.loan.interest_rate * 100:.1f}%"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content="-# Use `/loan repay` to pay back your loan."),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    class RepayLoanLayoutView(discord.ui.LayoutView):
        def __init__(self, response: RepayLoanCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: RepayLoanCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            currency = await self.response.server_config.get_default_currency_symbol()
            fully_repaid = self.response.loan.balance_remaining == 0
            items = [
                discord.ui.TextDisplay(content="## 🏦 Loan Payment Made"),
                discord.ui.Separator(),
                discord.ui.TextDisplay(content=f"**Amount Paid:** {currency}{Helpers.format_cash_amount(self.response.amount_paid)}"),
                discord.ui.TextDisplay(content=f"**Remaining Balance:** {currency}{Helpers.format_cash_amount(self.response.loan.balance_remaining)}"),
            ]
            if fully_repaid:
                items.append(discord.ui.Separator())
                items.append(discord.ui.TextDisplay(content="✅ Your loan has been fully repaid!"))
            self.add_item(
                discord.ui.Container(
                    *items,
                    accent_color=discord.Color.green() if fully_repaid else discord.Color.blue(),
                    spoiler=False
                )
            )


    class ExchangeLayoutView(discord.ui.LayoutView):
        def __init__(self, response: ExchangeCommandResponse | None = None):
            self.response = response
            super().__init__()

        @classmethod
        async def create(cls, response: ExchangeCommandResponse):
            view = cls(response)
            await view._build()
            return view

        async def _build(self):
            rate = self.response.exchange_rate
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(content="## 💱 Currency Exchanged"),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(content=f"**Spent (Currency {rate.from_currency_id}):** {Helpers.format_cash_amount(self.response.amount_spent)}"),
                    discord.ui.TextDisplay(content=f"**Received (Currency {rate.to_currency_id}):** {Helpers.format_cash_amount(self.response.amount_received)}"),
                    discord.ui.TextDisplay(content=f"**Rate:** {rate.rate:.4f}"),
                    accent_color=discord.Color.blue(),
                    spoiler=False
                )
            )


    @staticmethod
    async def get_stocks_view(interaction: Interaction, response: GetStocksQueryResponse):
        return await DiscordEconomyEmbed.StocksLayoutView.create(response)

    @staticmethod
    async def get_buy_stock_view(interaction: Interaction, response: BuyStockCommandResponse):
        return await DiscordEconomyEmbed.BuyStockLayoutView.create(response)

    @staticmethod
    async def get_pay_dividends_view(interaction: Interaction, response: PayDividendsCommandResponse):
        return await DiscordEconomyEmbed.PayDividendsLayoutView.create(response)

    @staticmethod
    async def get_take_loan_view(interaction: Interaction, response: TakeLoanCommandResponse):
        return await DiscordEconomyEmbed.TakeLoanLayoutView.create(response)

    @staticmethod
    async def get_repay_loan_view(interaction: Interaction, response: RepayLoanCommandResponse):
        return await DiscordEconomyEmbed.RepayLoanLayoutView.create(response)

    @staticmethod
    async def get_exchange_view(interaction: Interaction, response: ExchangeCommandResponse):
        return await DiscordEconomyEmbed.ExchangeLayoutView.create(response)
