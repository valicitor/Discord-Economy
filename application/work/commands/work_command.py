from datetime import datetime, timezone
import random

from attr import dataclass

from infrastructure import PlayerBalanceRepository, PlayerActionRepository, BusinessRepository, ActionRepository, BusinessStockRepository, BusinessResourceRepository, ResourceNodeRepository, LocationRepository, RecipeRepository, RecipeIngredientRepository, ItemRepository
from application.services.helpers import Helpers

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import PlayerAction, Business, Action, BusinessResource, CreateFailedException, UpdateFailedException, OnCooldownException

_SPECIAL_ACTION_TYPES = {"Prospect", "Extract", "Process", "Haul", "Restock"}
_WORK_ACTION_TYPES    = ["Work", "Prospect", "Extract", "Process", "Haul", "Restock"]

@dataclass
class WorkCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    work_type: str

@dataclass
class WorkCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    action_success: bool
    business: Business
    action: Action
    wage: int
    fine: int
    discovered_node: object = None
    extracted_resource: object = None
    processed_output: object = None
    hauled_transfer: object = None
    restocked_item: object = None

class WorkCommand:

    def __init__(self, request: WorkCommandRequest):
        self.request = request

    async def execute(self) -> WorkCommandResponse:
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.player_action_repository = await PlayerActionRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()
        self.action_repository = await ActionRepository().get_instance()
        self.business_stock_repository = await BusinessStockRepository().get_instance()
        self.business_resource_repository = await BusinessResourceRepository().get_instance()
        self.resource_node_repository = await ResourceNodeRepository().get_instance()
        self.location_repository = await LocationRepository().get_instance()
        self.recipe_repository = await RecipeRepository().get_instance()
        self.recipe_ingredient_repository = await RecipeIngredientRepository().get_instance()
        self.item_repository = await ItemRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        async with self.player_action_repository.transaction():
            last_action = await self.player_action_repository.get_last_action_by_type(self.request.work_type, player_profile.player.player_id)
            if last_action:
                last_used_at = datetime.fromisoformat(last_action.last_used_at)
                if last_used_at.tzinfo is None:
                    last_used_at = last_used_at.replace(tzinfo=timezone.utc)
                cooldown_seconds = last_action.cooldown_seconds
                now_utc = datetime.now(timezone.utc).replace(microsecond=0)
                if (last_used_at.timestamp() + cooldown_seconds) > now_utc.timestamp():
                    time_remaining_seconds = int((last_used_at.timestamp() + cooldown_seconds) - now_utc.timestamp())
                    raise OnCooldownException(f"You are on cooldown. Please wait {Helpers.format_countdown(time_remaining_seconds)} before working again.")

            businesses = await self.business_repository.get_all_within_range(x=player_profile.player.x, y=player_profile.player.y, server_id=server_config.server.server_id)
            if not businesses:
                return WorkCommandResponse(success=False, server_config=server_config, player=player_profile, action_success=False, business=None, action=None, wage=0, fine=0)

            rng_business = random.choice(businesses)

            query_type = _WORK_ACTION_TYPES if self.request.work_type == "Work" else self.request.work_type
            actions = await self.action_repository.get_all_by_business_id(action_type=query_type, business_id=rng_business.business_id)
            if not actions:
                return WorkCommandResponse(success=False, server_config=server_config, player=player_profile, action_success=False, business=None, action=None, wage=0, fine=0)

            rng_action = random.choice(actions)

            player_action = PlayerAction(
                player_id=player_profile.player.player_id,
                action_id=rng_action.action_id,
                type=rng_action.type,
                cooldown_seconds=rng_action.cooldown_seconds
            )
            action_created = await self.player_action_repository.insert(player_action)
            if not action_created:
                raise CreateFailedException("Player action already exists. Please wait before trying again.")

            action_success = random.uniform(0, 1) < rng_action.success_rate
            risk = random.uniform(0, rng_action.risk_rate)

            requirements = await self.business_resource_repository.get_requirements(rng_business.business_id)
            if not all(req.quantity >= req.required_quantity for req in requirements):
                action_success = False

            # Pre-fetch data for special action types so they influence action_success before wage calc
            discovered_node = None
            extracted_resource = None
            processed_output = None
            hauled_transfer = None
            restocked_item = None
            location = None
            undiscovered_nodes = []
            discovered_nodes = []
            recipe = None
            ingredient_resources = []
            haul_data = None
            restock_pair = None

            if rng_action.type in ("Prospect", "Extract"):
                location = await self.location_repository.get_by_coordinates(rng_business.x, rng_business.y, server_config.server.server_id)
                if not location:
                    action_success = False
                elif rng_action.type == "Prospect":
                    undiscovered_nodes = await self.resource_node_repository.get_undiscovered_by_location(location.location_id)
                    if not undiscovered_nodes:
                        action_success = False
                elif rng_action.type == "Extract":
                    discovered_nodes = await self.resource_node_repository.get_discovered_by_location(location.location_id)
                    if not discovered_nodes:
                        action_success = False

            elif rng_action.type == "Process":
                recipes = await self.recipe_repository.get_all_by_business(rng_business.business_id)
                if not recipes:
                    action_success = False
                else:
                    recipe = random.choice(recipes)
                    ingredients = await self.recipe_ingredient_repository.get_all_by_recipe(recipe.recipe_id)
                    for ing in ingredients:
                        br = await self.business_resource_repository.get_by_business_type(rng_business.business_id, ing.resource_type)
                        if not br or br.quantity < ing.quantity:
                            action_success = False
                            break
                        ingredient_resources.append((ing, br))

            elif rng_action.type == "Haul":
                source_resources = await self.business_resource_repository.get_all_by_business(rng_business.business_id)
                source_available = [r for r in source_resources if r.quantity > 0]
                if not source_available:
                    action_success = False
                else:
                    demanded = await self.business_resource_repository.get_demanded_by_server(server_config.server.server_id, rng_business.business_id)
                    source_types = {r.resource_type for r in source_available}
                    matched_demand = [d for d in demanded if d.resource_type in source_types]
                    if not matched_demand:
                        action_success = False
                    else:
                        haul_dest = random.choice(matched_demand)
                        haul_source = next(r for r in source_available if r.resource_type == haul_dest.resource_type)
                        dest_business = await self.business_repository.get_by_id(haul_dest.business_id)
                        haul_data = (haul_source, haul_dest, dest_business)

            elif rng_action.type == "Restock":
                source_resources = await self.business_resource_repository.get_all_by_business(rng_business.business_id)
                restockable = []
                for res in source_resources:
                    if res.quantity > 0:
                        item = await self.item_repository.get_by_name_and_business(res.resource_type, rng_business.business_id)
                        if item:
                            restockable.append((res, item))
                if not restockable:
                    action_success = False
                else:
                    restock_pair = random.choice(restockable)

            wage = int(rng_action.base_reward * (1 + risk)) if action_success else 0
            fine = int(rng_action.fine_amount * (1 + risk)) if not action_success else 0

            business_stock = await self.business_stock_repository.get_by_business_id(rng_business.business_id)
            if business_stock:
                delta = 5 if action_success else -5
                business_stock.market_points = max(0, min(200, business_stock.market_points + delta))
                await self.business_stock_repository.update(business_stock)

            if action_success:
                if rng_action.type == "Prospect":
                    node = random.choice(undiscovered_nodes)
                    node.discovered = True
                    await self.resource_node_repository.update(node)
                    discovered_node = node
                elif rng_action.type == "Extract":
                    node = random.choice(discovered_nodes)
                    node.quantity = max(0, node.quantity - 1)
                    await self.resource_node_repository.update(node)
                    br = await self.business_resource_repository.get_by_business_type(rng_business.business_id, node.resource_type)
                    if br:
                        br.quantity += 1
                        await self.business_resource_repository.update(br)
                    else:
                        br = BusinessResource(business_id=rng_business.business_id, resource_type=node.resource_type, quantity=1)
                        await self.business_resource_repository.insert(br)
                    extracted_resource = br
                elif rng_action.type == "Process":
                    for ing, br in ingredient_resources:
                        br.quantity -= ing.quantity
                        await self.business_resource_repository.update(br)
                    output_br = await self.business_resource_repository.get_by_business_type(rng_business.business_id, recipe.output_resource_type)
                    if output_br:
                        output_br.quantity += recipe.output_quantity
                        await self.business_resource_repository.update(output_br)
                    else:
                        output_br = BusinessResource(business_id=rng_business.business_id, resource_type=recipe.output_resource_type, quantity=recipe.output_quantity)
                        await self.business_resource_repository.insert(output_br)
                    processed_output = (recipe, output_br)
                elif rng_action.type == "Haul":
                    haul_source, haul_dest, dest_business = haul_data
                    haul_source.quantity -= 1
                    haul_dest.quantity += 1
                    await self.business_resource_repository.update(haul_source)
                    await self.business_resource_repository.update(haul_dest)
                    hauled_transfer = (haul_source.resource_type, dest_business)
                elif rng_action.type == "Restock":
                    res, item = restock_pair
                    res.quantity -= 1
                    item.stock = (item.stock or 0) + 1
                    await self.business_resource_repository.update(res)
                    await self.item_repository.update(item)
                    restocked_item = (res, item)
                elif rng_action.type not in _SPECIAL_ACTION_TYPES:
                    for req in requirements:
                        req.quantity = max(0, req.quantity - 1)
                        await self.business_resource_repository.update(req)
                    all_resources = await self.business_resource_repository.get_all_by_business(rng_business.business_id)
                    for res in all_resources:
                        if res.required_quantity == 0:
                            res.quantity += 1
                            await self.business_resource_repository.update(res)

            _, default_currency_id = server_config.server_settings.get_by_key("default_currency_id")
            j, player_balance = player_profile.balances.get_by_currency_id(int(default_currency_id.value))

            player_balance.balance = int(player_balance.balance) + wage - fine

            balance_updated = await self.player_balance_repository.update(player_balance=player_balance)
            if not balance_updated:
                raise UpdateFailedException("Failed to update player balance. Please try again.")

            player_profile.balances[j] = player_balance

        return WorkCommandResponse(success=balance_updated, server_config=server_config, player=player_profile, action_success=action_success, business=rng_business, action=rng_action, wage=wage, fine=fine, discovered_node=discovered_node, extracted_resource=extracted_resource, processed_output=processed_output, hauled_transfer=hauled_transfer, restocked_item=restocked_item)
