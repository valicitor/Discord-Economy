import math

from attr import dataclass

from infrastructure import (
    PlayerRepository, PlayerBalanceRepository, BankAccountRepository,
    PlayerActionRepository, PlayerInventoryRepository, PlayerUnitRepository,
    FactionRepository, FactionMemberRepository,
)
from application import (
    DiscordGuild, ServerConfig, PlayerProfile, PlayerFaction,
    PlayerBalancesCollection, PlayerBankAccountsCollection,
    PlayerInventoryCollection, PlayerUnitCollection, PlayerActionsCollection,
)
from application.services.helpers import Helpers

@dataclass
class GetLeaderboardQueryRequest:
    guild: DiscordGuild
    page: int
    sort_by: str
    limit: int

@dataclass
class GetLeaderboardQueryResponse:
    success: bool
    server_config: ServerConfig
    players: list[PlayerProfile]
    page: int
    max_pages: int
    sort_by: str
    limit: int

class GetLeaderboardQuery:

    def __init__(self, request: GetLeaderboardQueryRequest):
        self.request = request

    async def execute(self) -> GetLeaderboardQueryResponse:
        player_repo = await PlayerRepository().get_instance()
        balance_repo = await PlayerBalanceRepository().get_instance()
        bank_account_repo = await BankAccountRepository().get_instance()
        action_repo = await PlayerActionRepository().get_instance()
        inventory_repo = await PlayerInventoryRepository().get_instance()
        unit_repo = await PlayerUnitRepository().get_instance()
        faction_repo = await FactionRepository().get_instance()
        faction_member_repo = await FactionMemberRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        count = await player_repo.get_count(server_config.server.server_id)
        if count == 0:
            return GetLeaderboardQueryResponse(success=True, server_config=server_config, players=[], page=1, max_pages=1, limit=self.request.limit, sort_by=self.request.sort_by)

        max_pages = math.ceil(count / self.request.limit)
        if self.request.page > max_pages:
            self.request.page = 1

        players = await player_repo.get_leaderboard(server_config.server.server_id, self.request.page, self.request.sort_by, self.request.limit)

        async def _build_profile(player) -> PlayerProfile:
            balances = await balance_repo.get_all(player_id=player.player_id)
            bank_accounts = await bank_account_repo.get_all(player_id=player.player_id)
            actions = await action_repo.get_all_by_player_id(player_id=player.player_id)
            inventory = await inventory_repo.get_all_by_player_id(player_id=player.player_id)
            units = await unit_repo.get_all_by_player_id(player_id=player.player_id)
            faction_member = await faction_member_repo.get_by_player_id(player.player_id)
            faction = await faction_repo.get_by_id(faction_member.faction_id) if faction_member else None
            return PlayerProfile(
                player=player,
                faction=PlayerFaction(faction.faction_id, faction.name, faction.description, faction.color) if faction else None,
                balances=PlayerBalancesCollection(balances),
                bank_accounts=PlayerBankAccountsCollection(bank_accounts),
                inventory=PlayerInventoryCollection(inventory),
                units=PlayerUnitCollection(units),
                actions=PlayerActionsCollection(actions),
            )

        player_profiles = []
        for p in players:
            player_profiles.append(await _build_profile(p))

        return GetLeaderboardQueryResponse(success=True, server_config=server_config, players=list(player_profiles), page=self.request.page, max_pages=max_pages, limit=self.request.limit, sort_by=self.request.sort_by)
