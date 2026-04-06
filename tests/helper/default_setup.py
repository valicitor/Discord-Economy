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
    RaceRepository,
    RaceStatRepository,
    EquipmentRepository,
    EquipmentStatRepository,
    UnitRepository,
    UnitStatRepository,
    VehicleRepository,
    VehicleStatRepository,
    BusinessRepository,
    ActionRepository,
    KeywordRepository
)
from application import DiscordGuild, DiscordUser
from application.helpers.ensure_user import ensure_guild_and_users

class DefaultSetup:

    async def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")
        self.faction_repository = FactionRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")
        self.faction_member_repository = FactionMemberRepository(db_path=":memory:")
        self.player_action_repository = PlayerActionRepository(db_path=":memory:")

        self.business_repository = BusinessRepository(db_path=":memory:")
        self.action_repository = ActionRepository(db_path=":memory:")
        self.POI_repository = PointOfInterestRepository(db_path=":memory:")
        self.location_repository = LocationRepository(db_path=":memory:")
        self.equipment_repository = EquipmentRepository(db_path=":memory:")
        self.equipment_stat_repository = EquipmentStatRepository(db_path=":memory:")
        self.race_repository = RaceRepository(db_path=":memory:")
        self.race_stat_repository = RaceStatRepository(db_path=":memory:")
        self.unit_repository = UnitRepository(db_path=":memory:")
        self.unit_stat_repository = UnitStatRepository(db_path=":memory:")
        self.vehicle_repository = VehicleRepository(db_path=":memory:")
        self.vehicle_stat_repository = VehicleStatRepository(db_path=":memory:")
        self.keyword_repository = KeywordRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user1 = DiscordUser(user_id=67900, name="TestUser1", display_avatar="avatar_url")
        self.discord_user2 = DiscordUser(user_id=67901, name="TestUser2", display_avatar="avatar_url")
        self.discord_user3 = DiscordUser(user_id=67902, name="TestUser3", display_avatar="avatar_url")

        self.server_config, [self.player_profile1, self.player_profile2, self.player_profile3] = await ensure_guild_and_users(self.discord_guild, [self.discord_user1, self.discord_user2, self.discord_user3])

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

        _, enemy_faction_id = await self.faction_repository.add(Faction(name="Enemy Faction", description="Enemy", color="#FF0000", owner_id=self.player_profile3.player.player_id, server_id=self.server_config.server.server_id))
        await self.faction_member_repository.delete_by_player_id(self.player_profile3.player.player_id)  # Remove existing faction membership
        _, member_id = await  self.faction_member_repository.add(FactionMember(faction_id=enemy_faction_id, player_id=self.player_profile3.player.player_id, role="Leader"))

        _, ally_faction_id = await self.faction_repository.add(Faction(name="Ally Faction", description="Ally", color="#00FF00", owner_id=self.player_profile2.player.player_id, server_id=self.server_config.server.server_id))
        await self.faction_member_repository.delete_by_player_id(self.player_profile2.player.player_id)  # Remove existing faction membership
        _, member_id = await self.faction_member_repository.add(FactionMember(faction_id=ally_faction_id, player_id=self.player_profile2.player.player_id, role="Leader"))

        _, ally_faction_id = await self.faction_repository.add(Faction(name="Third Faction", description="Someone else", color="#0000FF", owner_id=self.player_profile1.player.player_id, server_id=self.server_config.server.server_id))
        await self.faction_member_repository.delete_by_player_id(self.player_profile1.player.player_id)  # Remove existing faction membership
        _, member_id = await self.faction_member_repository.add(FactionMember(faction_id=ally_faction_id, player_id=self.player_profile1.player.player_id, role="Leader"))

        location = (await self.location_repository.get_all())[2]
        location.owner_player_id = self.player_profile1.player.player_id
        await self.location_repository.update(location)

        location = (await self.location_repository.get_all())[7]
        location.owner_player_id = self.player_profile1.player.player_id
        await self.location_repository.update(location)

        location = (await self.location_repository.get_all())[3]
        location.owner_player_id = self.player_profile2.player.player_id
        await self.location_repository.update(location)

        location = (await self.location_repository.get_all())[5]
        location.owner_player_id = self.player_profile2.player.player_id
        await self.location_repository.update(location)

        location = (await self.location_repository.get_all())[0]
        location.owner_player_id = self.player_profile3.player.player_id
        await self.location_repository.update(location)

        location = (await self.location_repository.get_all())[8]
        location.owner_player_id = self.player_profile3.player.player_id
        await self.location_repository.update(location)

    async def tearDown(self):
        # Remove test user from the database
        await self.player_action_repository.delete_all(self.player_profile1.player.player_id)
        await self.player_action_repository.delete_all(self.player_profile2.player.player_id)
        await self.player_action_repository.delete_all(self.player_profile3.player.player_id)
        await self.faction_member_repository.delete_by_player_id(self.player_profile1.player.player_id)
        await self.faction_member_repository.delete_by_player_id(self.player_profile2.player.player_id)
        await self.faction_member_repository.delete_by_player_id(self.player_profile3.player.player_id)

        await self.bank_account_repository.delete_all(self.player_profile1.player.player_id)
        await self.player_balance_repository.delete_all(self.player_profile1.player.player_id)
        await self.player_repository.delete(self.player_profile1.player)

        await self.bank_account_repository.delete_all(self.player_profile2.player.player_id)
        await self.player_balance_repository.delete_all(self.player_profile2.player.player_id)
        await self.player_repository.delete(self.player_profile2.player)

        await self.bank_account_repository.delete_all(self.player_profile3.player.player_id)
        await self.player_balance_repository.delete_all(self.player_profile3.player.player_id)
        await self.player_repository.delete(self.player_profile3.player)

        await self.business_repository.delete_all(self.server_config.server.server_id)
        await self.action_repository.delete_all()
        await self.POI_repository.delete_all(self.server_config.server.server_id)
        await self.location_repository.delete_all()
        await self.equipment_repository.delete_all(self.server_config.server.server_id)
        await self.equipment_stat_repository.delete_all()
        await self.race_repository.delete_all(self.server_config.server.server_id)
        await self.race_stat_repository.delete_all()
        await self.unit_repository.delete_all(self.server_config.server.server_id)
        await self.unit_stat_repository.delete_all()
        await self.vehicle_repository.delete_all(self.server_config.server.server_id)
        await self.vehicle_stat_repository.delete_all()
        await self.keyword_repository.delete_all(self.server_config.server.server_id)

        await self.faction_repository.delete_all(self.server_config.server.server_id)
        await self.bank_repository.delete_all(self.server_config.server.server_id)
        await self.currency_repository.delete_all(self.server_config.server.server_id)
        await self.server_setting_repository.delete_all(self.server_config.server.server_id)
        await self.server_repository.delete(self.server_config.server)