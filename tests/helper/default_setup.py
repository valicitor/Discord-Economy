from domain import (
    Faction,
    FactionMember
)
from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository,
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    BankAccountRepository,
    FactionRepository,
    FactionMemberRepository,
    PlayerActionRepository,
    PointOfInterestRepository,
    LocationRepository,
    CatalogueRepository,
    BusinessRepository,
    ActionRepository,
    KeywordRepository,
    ItemRepository,
    PlayerInventoryRepository,
    PlayerUnitRepository
)
from application import DiscordGuild, DiscordUser
from application.helpers.helpers import Helpers

class DefaultSetup:

    @classmethod
    async def setUpClass(cls):
        cls.server_repository = await ServerRepository().get_instance(db_path=":memory:")
        cls.server_setting_repository = await ServerSettingRepository().get_instance(db_path=":memory:")
        cls.currency_repository = await CurrencyRepository().get_instance(db_path=":memory:")
        cls.bank_repository = await BankRepository().get_instance(db_path=":memory:")
        cls.faction_repository = await FactionRepository().get_instance(db_path=":memory:")

        cls.player_repository = await PlayerRepository().get_instance(db_path=":memory:")
        cls.player_balance_repository = await PlayerBalanceRepository().get_instance(db_path=":memory:")
        cls.bank_account_repository = await BankAccountRepository().get_instance(db_path=":memory:")
        cls.faction_member_repository = await FactionMemberRepository().get_instance(db_path=":memory:")
        cls.player_action_repository = await PlayerActionRepository().get_instance(db_path=":memory:")
        cls.player_inventory_repository = await PlayerInventoryRepository().get_instance(db_path=":memory:")
        cls.player_unit_repository = await PlayerUnitRepository().get_instance(db_path=":memory:")

        cls.business_repository = await BusinessRepository().get_instance(db_path=":memory:")
        cls.action_repository = await ActionRepository().get_instance(db_path=":memory:")
        cls.POI_repository = await PointOfInterestRepository().get_instance(db_path=":memory:")
        cls.location_repository = await LocationRepository().get_instance(db_path=":memory:")

        cls.catalogue_repository = await CatalogueRepository().get_instance(db_path=":memory:")
        cls.keyword_repository = await KeywordRepository().get_instance(db_path=":memory:")
        cls.items_repository = await ItemRepository().get_instance(db_path=":memory:")

    @classmethod
    async def tearDownClass(cls):
        await cls.server_repository.close_all()
        await cls.server_setting_repository.close_all()
        await cls.currency_repository.close_all()
        await cls.bank_repository.close_all()
        await cls.faction_repository.close_all()

        await cls.player_repository.close_all()
        await cls.player_balance_repository.close_all()
        await cls.bank_account_repository.close_all()
        await cls.faction_member_repository.close_all()
        await cls.player_action_repository.close_all()
        await cls.player_inventory_repository.close_all()
        await cls.player_unit_repository.close_all()

        await cls.business_repository.close_all()
        await cls.action_repository.close_all()
        await cls.POI_repository.close_all()
        await cls.location_repository.close_all()

        await cls.catalogue_repository.close_all()
        await cls.keyword_repository.close_all()
        await cls.items_repository.close_all()

    async def setUp(self):
        await self.server_repository.clear_all()
        await self.server_setting_repository.clear_all()
        await self.currency_repository.clear_all()
        await self.bank_repository.clear_all()
        await self.faction_repository.clear_all()

        await self.player_repository.clear_all()
        await self.player_balance_repository.clear_all()
        await self.bank_account_repository.clear_all()
        await self.faction_member_repository.clear_all()
        await self.player_action_repository.clear_all()
        await self.player_inventory_repository.clear_all()
        await self.player_unit_repository.clear_all()

        await self.business_repository.clear_all()
        await self.action_repository.clear_all()
        await self.POI_repository.clear_all()
        await self.location_repository.clear_all()

        await self.catalogue_repository.clear_all()
        await self.keyword_repository.clear_all()
        await self.items_repository.clear_all()

    async def setupData(self):
        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user1 = DiscordUser(user_id=67900, name="TestUser1", display_avatar="avatar_url")
        self.discord_user2 = DiscordUser(user_id=67901, name="TestUser2", display_avatar="avatar_url")
        self.discord_user3 = DiscordUser(user_id=67902, name="TestUser3", display_avatar="avatar_url")

        self.server_config, [self.player_profile1, self.player_profile2, self.player_profile3] = await Helpers.ensure_guild_and_users(self.discord_guild, [self.discord_user1, self.discord_user2, self.discord_user3])

        self.player_profile1.balances[0].balance = 1500
        await self.player_balance_repository.update(self.player_profile1.balances[0])
        self.player_profile1.bank_accounts[0].balance = 1500
        await self.bank_account_repository.update(self.player_profile1.bank_accounts[0])

        self.player_profile2.balances[0].balance = 50
        await self.player_balance_repository.update(self.player_profile2.balances[0])
        self.player_profile2.bank_accounts[0].balance = 2000
        await self.bank_account_repository.update(self.player_profile2.bank_accounts[0])

        self.player_profile3.balances[0].balance = 2000
        await self.player_balance_repository.update(self.player_profile3.balances[0])
        self.player_profile3.bank_accounts[0].balance = 25
        await self.bank_account_repository.update(self.player_profile3.bank_accounts[0])

        enemy_faction_id = await self.faction_repository.insert(Faction(name="Enemy Faction", description="Enemy", color="#FF0000", owner_id=self.player_profile3.player.player_id, server_id=self.server_config.server.server_id))
        await self.faction_member_repository.delete_by_player_id(self.player_profile3.player.player_id)  # Remove existing faction membership
        member_id = await  self.faction_member_repository.insert(FactionMember(faction_id=enemy_faction_id, player_id=self.player_profile3.player.player_id, role="Leader"))

        ally_faction_id = await self.faction_repository.insert(Faction(name="Ally Faction", description="Ally", color="#00FF00", owner_id=self.player_profile2.player.player_id, server_id=self.server_config.server.server_id))
        await self.faction_member_repository.delete_by_player_id(self.player_profile2.player.player_id)  # Remove existing faction membership
        member_id = await self.faction_member_repository.insert(FactionMember(faction_id=ally_faction_id, player_id=self.player_profile2.player.player_id, role="Leader"))

        ally_faction_id = await self.faction_repository.insert(Faction(name="Third Faction", description="Someone else", color="#0000FF", owner_id=self.player_profile1.player.player_id, server_id=self.server_config.server.server_id))
        await self.faction_member_repository.delete_by_player_id(self.player_profile1.player.player_id)  # Remove existing faction membership
        member_id = await self.faction_member_repository.insert(FactionMember(faction_id=ally_faction_id, player_id=self.player_profile1.player.player_id, role="Leader"))

        locations = await self.location_repository.get_all()

        location = locations[2]
        location.owner_player_id = self.player_profile1.player.player_id
        await self.location_repository.update(location)

        location = locations[7]
        location.owner_player_id = self.player_profile1.player.player_id
        await self.location_repository.update(location)

        location = locations[3]
        location.owner_player_id = self.player_profile2.player.player_id
        await self.location_repository.update(location)

        location = locations[5]
        location.owner_player_id = self.player_profile2.player.player_id
        await self.location_repository.update(location)

        location = locations[0]
        location.owner_player_id = self.player_profile3.player.player_id
        await self.location_repository.update(location)

        location = locations[8]
        location.owner_player_id = self.player_profile3.player.player_id
        await self.location_repository.update(location)