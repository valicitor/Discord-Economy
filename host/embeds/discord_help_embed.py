import discord
from config import BOT_NAME, BOT_VERSION

class DiscordHelpEmbed:
    COMMAND_INFO = {
        # Admin — server
        "admin setup":                    {"description": "Initialize the server. Optionally seed with default world data.\n**Options:** `theme` star_wars/halo/none", "examples": ["/admin setup theme:star_wars"]},
        "admin server":                   {"description": "Display the server's current configuration and default settings.", "examples": ["/admin server"]},
        # Admin — balance
        "admin balance add":              {"description": "Add currency to a member's Cash or Bank account.", "examples": ["/admin balance add @User 500", "/admin balance add @User 1000 account_type:Bank"]},
        "admin balance set":              {"description": "Set a member's Cash or Bank balance to a specific amount.", "examples": ["/admin balance set @User 1000"]},
        # Admin — currency
        "admin currency symbol":          {"description": "Change the currency symbol shown on all balance displays.", "examples": ["/admin currency symbol currency_symbol:$"]},
        "admin currency exchange-rate":   {"description": "Set the exchange rate between two currencies (from → to).", "examples": ["/admin currency exchange-rate from_currency_id:1 to_currency_id:2 rate:1.5"]},
        # Admin — business
        "admin business create":          {"description": "Create a new in-world business at given coordinates. `range` is optional — leave blank for unlimited range.", "examples": ["/admin business create name:Foundry type:Manufacturing x:100 y:200 range:500"]},
        "admin business edit":            {"description": "Update an existing business's name, location, or range.", "examples": ["/admin business edit business_id:1 range:800"]},
        "admin business stock-enable":    {"description": "Enable public stock trading for a business at a set base price and dividend rate.", "examples": ["/admin business stock-enable business_id:1 base_price:100 dividend_rate:0.05"]},
        "admin business pay-dividends":   {"description": "(Admin) Pay out dividends to all shareholders of a business.", "examples": ["/admin business pay-dividends business_id:1"]},
        # Admin — item
        "admin item create":              {"description": "Add a shop item linked to a catalogue entry. Optionally restrict to a business with `business_id`.", "examples": ["/admin item create catalogue_id:1 name:Sword price:500", "/admin item create catalogue_id:3 name:Clone Trooper price:1000 business_id:2"]},
        "admin item edit":                {"description": "Update a shop item's name, price, stock, or business assignment.", "examples": ["/admin item edit item_id:3 price:750"]},
        # Admin — world
        "admin world bank-create":        {"description": "Create a new bank at a location. `range` is optional.", "examples": ["/admin world bank-create name:Central Bank interest_rate:0.02 x:0 y:0"]},
        "admin world bank-edit":          {"description": "Edit a bank's name, interest rate, or location.", "examples": ["/admin world bank-edit bank_id:1 interest_rate:0.03"]},
        "admin world travel-speed":       {"description": "Set how fast transports travel (units per minute).", "examples": ["/admin world travel-speed speed:10"]},
        "admin world setting":            {"description": "Set an arbitrary server setting key/value.", "examples": ["/admin world setting key:default_currency_id value:1"]},
        # Admin — resource nodes
        "admin resource-node create":     {"description": "Create a resource node at a location. `discovered` controls whether players can see it immediately.", "examples": ["/admin resource-node create location_id:1 resource_type:Beskar max_quantity:500 regen_rate:10"]},
        "admin resource-node edit":       {"description": "Edit a resource node's type, max quantity, or regen rate.", "examples": ["/admin resource-node edit node_id:3 regen_rate:20"]},
        "admin resource-node toggle":     {"description": "Toggle a node between discoverable (hidden) and available (visible).", "examples": ["/admin resource-node toggle node_id:3"]},
        "admin resource-node delete":     {"description": "Permanently remove a resource node.", "examples": ["/admin resource-node delete node_id:3"]},
        # Admin — recipes
        "admin recipe create":        {"description": "Create a server-level recipe by name.", "examples": ["/admin recipe create name:Beskar Ingot"]},
        "admin recipe edit":          {"description": "Rename a recipe.", "examples": ["/admin recipe edit recipe_id:2 name:New Name"]},
        "admin recipe delete":        {"description": "Delete a recipe and all its inputs/outputs.", "examples": ["/admin recipe delete recipe_id:2"]},
        "admin recipe input-add":     {"description": "Add a catalogue item as an input to a recipe.", "examples": ["/admin recipe input-add recipe_id:2 catalogue_id:5 quantity:3"]},
        "admin recipe input-remove":  {"description": "Remove a catalogue input from a recipe.", "examples": ["/admin recipe input-remove recipe_id:2 catalogue_id:5"]},
        "admin recipe output-add":    {"description": "Add a catalogue item as an output of a recipe.", "examples": ["/admin recipe output-add recipe_id:2 catalogue_id:7 quantity:1"]},
        "admin recipe output-remove": {"description": "Remove a catalogue output from a recipe.", "examples": ["/admin recipe output-remove recipe_id:2 catalogue_id:7"]},
        # Admin — location policies
        "admin policy create":            {"description": "Set a governance policy for a location. All rates default to 0 / 1.0 if omitted.", "examples": ["/admin policy create location_id:1 tax_rate:0.05 interest_rate_modifier:1.2"]},
        "admin policy edit":              {"description": "Update one or more fields on a location's existing policy.", "examples": ["/admin policy edit location_id:1 smuggling_risk_modifier:2.0 import_restricted:True"]},
        "admin policy delete":            {"description": "Remove the governance policy from a location.", "examples": ["/admin policy delete location_id:1"]},
        # Balance
        "balance":                        {"description": "View your current Cash and Bank balances.", "examples": ["/balance"]},
        "pay":                            {"description": "Send currency from your Cash balance to another player.", "examples": ["/pay @User 200"]},
        "bank deposit":                   {"description": "Move currency from your Cash balance into your Bank account.", "examples": ["/bank deposit 500"]},
        "bank withdraw":                  {"description": "Move currency from your Bank account to your Cash balance.", "examples": ["/bank withdraw 200"]},
        "leaderboard":                    {"description": "Show the top players by Cash balance on this server.", "examples": ["/leaderboard"]},
        # Shop
        "shop browse":                    {"description": "Browse items available to buy. Only shows items near your location.", "examples": ["/shop browse", "/shop browse page:2 sort:Cost"]},
        "shop buy":                       {"description": "Purchase a shop item by name. You must be near the business that sells it.", "examples": ["/shop buy Clone Trooper", "/shop buy Clone Trooper quantity:3"]},
        "shop sell":                      {"description": "Sell an item or unit from your inventory back to the shop.", "examples": ["/shop sell DC-15A Blaster Rifle"]},
        "shop info":                      {"description": "View the detailed stats block for a catalogue item.", "examples": ["/shop info Clone Trooper"]},
        # Unit
        "unit create":                    {"description": "Create a named custom unit from a Race in your stored inventory.", "examples": ["/unit create unit_name:Alpha-1 race_name:Human"]},
        "unit equip":                     {"description": "Equip an item from your inventory to your character.", "examples": ["/unit equip Phase I Clone Armor"]},
        "unit unequip":                   {"description": "Unequip an item from your character, returning it to stored inventory.", "examples": ["/unit unequip Phase I Clone Armor"]},
        "unit unassign":                  {"description": "Remove equipment from a unit's slot, returning it to inventory.", "examples": ["/unit unassign unit_name:Alpha-1 slot_name:Primary"]},
        # Work
        "work":                           {"description": "Perform work at a nearby business to earn currency. Subject to cooldown.", "examples": ["/work"]},
        # Market
        "market stocks":                  {"description": "View your current stock portfolio and the value of each holding.", "examples": ["/market stocks"]},
        "market buy":                     {"description": "Buy shares of a tradeable business at the current market price.", "examples": ["/market buy business_id:1 quantity:10"]},
        "market exchange":                {"description": "Exchange one currency for another at the configured exchange rate.", "examples": ["/market exchange from_currency_id:1 to_currency_id:2 amount:100"]},
        "loan take":                      {"description": "Take a loan from the bank. You must be near the bank. Only one active loan at a time.", "examples": ["/loan take amount:1000"]},
        "loan repay":                     {"description": "Make a payment on your outstanding loan. You must be near the bank.", "examples": ["/loan repay amount:500"]},
        # Faction
        "faction create":                 {"description": "Create a new faction. You become the owner.", "examples": ["/faction create name:Clan Wren description:Mandalorian warriors color:#FF6600"]},
        "faction join":                   {"description": "Join an existing faction by name.", "examples": ["/faction join faction_name:Clan Wren"]},
        "faction leave":                  {"description": "Leave your current faction. Owners must disband instead.", "examples": ["/faction leave"]},
        "faction info":                   {"description": "View a faction's details and member list. Defaults to your own faction.", "examples": ["/faction info", "/faction info faction_name:Clan Wren"]},
        # Logistics
        "logistics garrison assign":      {"description": "Assign one of your units to garrison a named location.", "examples": ["/logistics garrison assign unit_name:Alpha-1 poi_name:Coruscant"]},
        "logistics garrison view":        {"description": "View all units you have garrisoned and their locations.", "examples": ["/logistics garrison view"]},
        "logistics maintenance pay":      {"description": "Pay maintenance costs for all your units.", "examples": ["/logistics maintenance pay"]},
        "logistics transport start":      {"description": "Start transporting a catalogue item between two businesses. You must be near the source.", "examples": ["/logistics transport start from_business_id:1 to_business_id:2 catalogue_id:3 quantity:10"]},
        "logistics transport complete":   {"description": "Collect all transports that have arrived at their destination.", "examples": ["/logistics transport complete"]},
    }

    @staticmethod
    def command_not_found(command_name: str) -> discord.Embed:
        return discord.Embed(
            title="❌ Command Not Found",
            description=f"Command `{command_name}` not found. Use `/help` to see all commands.",
            color=discord.Color.red()
        )

    @staticmethod
    def help_embed() -> discord.Embed:
        embed = discord.Embed(
            title=f"🤖 {BOT_NAME} Bot v{BOT_VERSION} — Help Menu",
            description="Use `/help <command>` for detailed info and examples on any command.\n​",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🏦 Balance & Banking",
            value="`/balance` `/pay` `/bank deposit` `/bank withdraw` `/leaderboard`",
            inline=False,
        )
        embed.add_field(
            name="🛒 Shop",
            value="`/shop browse` `/shop buy` `/shop sell` `/shop info`",
            inline=False,
        )
        embed.add_field(
            name="⚔️ Units & Equipment",
            value="`/unit create` `/unit equip` `/unit unequip` `/unit unassign`",
            inline=False,
        )
        embed.add_field(
            name="⚒️ Work",
            value="`/work`",
            inline=False,
        )
        embed.add_field(
            name="📈 Market & Loans",
            value="`/market stocks` `/market buy` `/market exchange` `/loan take` `/loan repay`",
            inline=False,
        )
        embed.add_field(
            name="⚔️ Faction",
            value="`/faction create` `/faction join` `/faction leave` `/faction info`",
            inline=False,
        )
        embed.add_field(
            name="🚚 Logistics",
            value="`/logistics garrison assign` `/logistics garrison view` `/logistics maintenance pay` `/logistics transport start` `/logistics transport complete`",
            inline=False,
        )
        embed.add_field(
            name="🔧 Admin",
            value="`/admin setup` `/admin server` `/admin balance` `/admin currency` `/admin business` `/admin item` `/admin world` `/admin resource-node` `/admin recipe` `/admin policy`",
            inline=False,
        )

        embed.set_footer(text="Use /help <command> for detailed information and examples")
        return embed

    @staticmethod
    def command_help(command_name: str) -> discord.Embed:
        info = DiscordHelpEmbed.COMMAND_INFO.get(command_name, {})

        embed = discord.Embed(
            title=f"ℹ️ /{command_name}",
            description=info.get("description", "No description available."),
            color=discord.Color.blue()
        )

        examples = info.get("examples")
        if examples:
            embed.add_field(
                name="Examples",
                value="\n".join(f"`{e}`" for e in examples),
                inline=False
            )

        return embed

    @staticmethod
    def version_embed() -> discord.Embed:
        embed = discord.Embed(
            title=f"🤖 {BOT_NAME} Bot Version",
            description=f"Current version: v{BOT_VERSION}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Thank you for using {BOT_NAME} Bot!")
        return embed

    @staticmethod
    def command_faq() -> discord.Embed:
        embed = discord.Embed(
            title=f"🤖 {BOT_NAME} Bot — FAQs",
            description="Common questions about the bot",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use /help <command> for detailed command information")
        return embed
