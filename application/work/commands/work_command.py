from datetime import datetime, timezone
import asyncio
import random

from attr import dataclass

from infrastructure import PlayerBalanceRepository, PlayerActionRepository, BusinessRepository, ActionRepository, BusinessStockRepository, BusinessInventoryRepository, ResourceNodeRepository, LocationRepository, RecipeRepository, RecipeInputRepository, RecipeOutputRepository, ItemRepository, CatalogueRepository
from application.services.helpers import Helpers

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import PlayerAction, Business, Action, BusinessInventory, CreateFailedException, UpdateFailedException, OnCooldownException

_WORK_ACTION_TYPES = ["Work", "Prospect", "Extract", "Process", "Haul", "Restock"]

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
        (
            self.player_balance_repository,
            self.player_action_repository,
            self.business_repository,
            self.action_repository,
            self.business_stock_repository,
            self.business_inventory_repository,
            self.resource_node_repository,
            self.location_repository,
            self.recipe_repository,
            self.recipe_input_repository,
            self.recipe_output_repository,
            self.item_repository,
            self.catalogue_repository,
        ) = await asyncio.gather(
            PlayerBalanceRepository().get_instance(),
            PlayerActionRepository().get_instance(),
            BusinessRepository().get_instance(),
            ActionRepository().get_instance(),
            BusinessStockRepository().get_instance(),
            BusinessInventoryRepository().get_instance(),
            ResourceNodeRepository().get_instance(),
            LocationRepository().get_instance(),
            RecipeRepository().get_instance(),
            RecipeInputRepository().get_instance(),
            RecipeOutputRepository().get_instance(),
            ItemRepository().get_instance(),
            CatalogueRepository().get_instance(),
        )

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
            recipe_inputs = []
            recipe_outputs = []
            input_resources = []
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
                if rng_business.recipe_id:
                    recipe = await self.recipe_repository.get_by_id(rng_business.recipe_id)

                if not recipe:
                    action_success = False
                else:
                    recipe_inputs = await self.recipe_input_repository.get_all_by_recipe(recipe.recipe_id)
                    recipe_outputs = await self.recipe_output_repository.get_all_by_recipe(recipe.recipe_id)

                    if not recipe_inputs or not recipe_outputs:
                        action_success = False
                    else:
                        # Bulk-load inventory for all recipe inputs in one pass
                        biz_inventory_all = await self.business_inventory_repository.get_all_by_business(rng_business.business_id)
                        biz_inventory_map = {i.catalogue_id: i for i in biz_inventory_all}
                        for inp in recipe_inputs:
                            inv = biz_inventory_map.get(inp.catalogue_id)
                            if not inv or inv.quantity < inp.quantity:
                                action_success = False
                                break
                            input_resources.append((inp, inv))

            elif rng_action.type == "Haul":
                source_inventory = await self.business_inventory_repository.get_all_by_business(rng_business.business_id)
                source_available = [i for i in source_inventory if i.quantity > 0]
                if not source_available:
                    action_success = False
                else:
                    source_catalogue_ids = {i.catalogue_id for i in source_available}
                    all_businesses = await self.business_repository.get_all(server_config.server.server_id)
                    candidate_businesses = [b for b in all_businesses if b.business_id != rng_business.business_id and b.recipe_id]

                    # Bulk-load all recipe inputs and destination inventory for candidate businesses
                    all_recipe_inputs = {}
                    for biz in candidate_businesses:
                        all_recipe_inputs[biz.recipe_id] = await self.recipe_input_repository.get_all_by_recipe(biz.recipe_id)

                    dest_catalogue_pairs = {
                        (biz.business_id, inp.catalogue_id)
                        for biz in candidate_businesses
                        for inp in all_recipe_inputs.get(biz.recipe_id, [])
                        if inp.catalogue_id in source_catalogue_ids
                    }
                    dest_inventories = {}
                    for (bid, cid) in dest_catalogue_pairs:
                        dest_inventories[(bid, cid)] = await self.business_inventory_repository.get_by_business_catalogue(bid, cid)

                    haul_candidates = []
                    for biz in candidate_businesses:
                        for req_input in all_recipe_inputs.get(biz.recipe_id, []):
                            if req_input.catalogue_id not in source_catalogue_ids:
                                continue
                            biz_inv = dest_inventories.get((biz.business_id, req_input.catalogue_id))
                            if not biz_inv or biz_inv.quantity < req_input.quantity:
                                src = next(i for i in source_available if i.catalogue_id == req_input.catalogue_id)
                                haul_candidates.append((src, biz_inv, biz, req_input.catalogue_id))
                    if not haul_candidates:
                        action_success = False
                    else:
                        chosen = random.choice(haul_candidates)
                        haul_data = chosen  # (src_inv, dest_inv_or_None, dest_business, catalogue_id)

            elif rng_action.type == "Restock":
                source_inventory = await self.business_inventory_repository.get_all_by_business(rng_business.business_id)
                nonempty_inventory = [i for i in source_inventory if i.quantity > 0]
                if not nonempty_inventory:
                    action_success = False
                else:
                    # Bulk-load all shop items for this business, then join in Python
                    all_items = await self.item_repository.get_all_by_business(rng_business.business_id)
                    items_by_catalogue = {item.catalogue_id: item for item in all_items}
                    restockable = [
                        (inv, items_by_catalogue[inv.catalogue_id])
                        for inv in nonempty_inventory
                        if inv.catalogue_id in items_by_catalogue
                    ]
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
                    catalogue_entry = await self.catalogue_repository.get_by_name(node.resource_type, server_config.server.server_id)
                    if catalogue_entry:
                        inv = await self.business_inventory_repository.get_by_business_catalogue(rng_business.business_id, catalogue_entry.catalogue_id)
                        if inv:
                            inv.quantity += 1
                            await self.business_inventory_repository.update(inv)
                        else:
                            inv = BusinessInventory(business_id=rng_business.business_id, catalogue_id=catalogue_entry.catalogue_id, quantity=1)
                            await self.business_inventory_repository.insert(inv)
                        extracted_resource = inv

                elif rng_action.type == "Process":
                    for inp, inv in input_resources:
                        inv.quantity -= inp.quantity
                        await self.business_inventory_repository.update(inv)
                    # Bulk-load current output inventory, then upsert in Python without per-row queries
                    output_catalogue_ids = {out.catalogue_id for out in recipe_outputs}
                    existing_out_inv = await self.business_inventory_repository.get_all_by_business(rng_business.business_id)
                    out_inv_map = {i.catalogue_id: i for i in existing_out_inv if i.catalogue_id in output_catalogue_ids}
                    output_entries = []
                    for out in recipe_outputs:
                        out_inv = out_inv_map.get(out.catalogue_id)
                        if out_inv:
                            out_inv.quantity += out.quantity
                            await self.business_inventory_repository.update(out_inv)
                        else:
                            out_inv = BusinessInventory(business_id=rng_business.business_id, catalogue_id=out.catalogue_id, quantity=out.quantity)
                            await self.business_inventory_repository.insert(out_inv)
                        output_entries.append(out_inv)
                    processed_output = (recipe, output_entries)

                elif rng_action.type == "Haul":
                    src_inv, dest_inv, dest_business, catalogue_id = haul_data
                    src_inv.quantity -= 1
                    await self.business_inventory_repository.update(src_inv)
                    if dest_inv:
                        dest_inv.quantity += 1
                        await self.business_inventory_repository.update(dest_inv)
                    else:
                        new_inv = BusinessInventory(business_id=dest_business.business_id, catalogue_id=catalogue_id, quantity=1)
                        await self.business_inventory_repository.insert(new_inv)
                    hauled_transfer = (catalogue_id, dest_business)

                elif rng_action.type == "Restock":
                    inv, item = restock_pair
                    inv.quantity -= 1
                    item.stock = (item.stock or 0) + 1
                    await self.business_inventory_repository.update(inv)
                    await self.item_repository.update(item)
                    restocked_item = (inv, item)

            _, default_currency_id = server_config.server_settings.get_by_key("default_currency_id")
            j, player_balance = player_profile.balances.get_by_currency_id(int(default_currency_id.value))

            player_balance.balance = int(player_balance.balance) + wage - fine

            balance_updated = await self.player_balance_repository.update(player_balance=player_balance)
            if not balance_updated:
                raise UpdateFailedException("Failed to update player balance. Please try again.")

            player_profile.balances[j] = player_balance

        return WorkCommandResponse(success=balance_updated, server_config=server_config, player=player_profile, action_success=action_success, business=rng_business, action=rng_action, wage=wage, fine=fine, discovered_node=discovered_node, extracted_resource=extracted_resource, processed_output=processed_output, hauled_transfer=hauled_transfer, restocked_item=restocked_item)
