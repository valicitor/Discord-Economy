from datetime import datetime, timezone


class EconomyTickService:
    """
    Resolves all time-based effects for a player or entity lazily, at the
    start of any command that needs current state.

    The bot has no background scheduler. Every accrual (loan interest,
    dividend credit, unit maintenance, resource node regen) is computed
    here from the elapsed seconds since the entity's last_updated_at
    timestamp, then persisted before the calling command proceeds.

    All methods must be idempotent: if elapsed <= 0 they return immediately
    without mutating anything, so calling twice within the same second is safe.

    Usage pattern inside a command:
        await EconomyTickService.tick_loans(player_id, server_config, repositories)
        # then execute the command's own action
    """

    @staticmethod
    def elapsed_seconds(last_updated_at: str | None) -> float:
        """Returns seconds since last_updated_at, or 0 if None/future."""
        if not last_updated_at:
            return 0.0
        try:
            last = datetime.fromisoformat(last_updated_at)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            delta = (datetime.now(timezone.utc) - last).total_seconds()
            return max(0.0, delta)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    async def tick_loans(player_id: int, default_currency_id: int, loan_repo, balance_repo) -> None:
        """
        Compounds interest on all active loans for a player and updates
        last_updated_at. Skips any loan with elapsed <= 0.
        """
        loans = await loan_repo.get_all_by_player_id(player_id, status="active")
        for loan in loans:
            elapsed = EconomyTickService.elapsed_seconds(loan.last_updated_at)
            if elapsed <= 0:
                continue
            elapsed_days = elapsed / 86400.0
            interest = loan.balance_remaining * loan.interest_rate * elapsed_days
            loan.balance_remaining = int(loan.balance_remaining + interest)
            await loan_repo.update(loan)

    @staticmethod
    async def tick_player_stocks(player_id: int, default_currency_id: int, stock_repo, business_stock_repo, balance_repo) -> None:
        """
        Accrues dividends for all stock holdings since last_updated_at and
        credits the player's default-currency balance.
        """
        stocks = await stock_repo.get_all_by_player_id(player_id)
        for ps in stocks:
            elapsed = EconomyTickService.elapsed_seconds(ps.last_updated_at)
            if elapsed <= 0:
                continue
            elapsed_days = elapsed / 86400.0
            business_stock = await business_stock_repo.get_by_business_id(ps.business_id)
            if not business_stock:
                continue
            payout = int(business_stock.current_price * business_stock.dividend_rate * ps.quantity * elapsed_days)
            if payout <= 0:
                continue
            balances = await balance_repo.get_all(player_id=player_id)
            balance = next((b for b in balances if b.currency_id == default_currency_id), None)
            if not balance:
                continue
            balance.balance = int(balance.balance) + payout
            await balance_repo.update(balance)
            await stock_repo.update(ps)

    @staticmethod
    async def tick_resource_node(node, node_repo) -> None:
        """
        Regenerates a single resource node up to its max_quantity based on
        regen_rate (units/day) and elapsed time since last_updated_at.
        """
        elapsed = EconomyTickService.elapsed_seconds(node.last_updated_at)
        if elapsed <= 0:
            return
        elapsed_days = elapsed / 86400.0
        regen = int(node.regen_rate * elapsed_days)
        if regen <= 0:
            return
        node.quantity = min(node.max_quantity, node.quantity + regen)
        await node_repo.update(node)
