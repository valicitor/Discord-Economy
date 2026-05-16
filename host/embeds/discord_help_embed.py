import discord
from config import BOT_NAME, BOT_VERSION

class DiscordHelpEmbed:
    COMMAND_INFO = {
        # Admin
        "admin setup":           {"description": "Initialize the server. Optionally seed with default world data.\n**Options:** `seed_data` True/False, `theme` star_wars/halo", "examples": ["/admin setup seed_data:True theme:star_wars"]},
        "admin server":          {"description": "Display the server's current configuration and default settings.", "examples": ["/admin server"]},
        "admin set-currency-symbol": {"description": "Change the currency symbol shown on all balance displays.", "examples": ["/admin set-currency-symbol currency_symbol:$"]},
        "admin add-balance":     {"description": "Add currency to a member's Cash or Bank account.", "examples": ["/admin add-balance @User 500", "/admin add-balance @User 1000 account_type:Bank"]},
        "admin set-balance":     {"description": "Set a member's Cash or Bank balance to a specific amount.", "examples": ["/admin set-balance @User 1000"]},
        "admin business create": {"description": "Create a new in-world business at given coordinates. `range` is optional — leave blank for unlimited range.", "examples": ["/admin business create name:Foundry type:Manufacturing x:100 y:200 range:500"]},
        "admin business edit":   {"description": "Update an existing business's name, location, or range.", "examples": ["/admin business edit business_id:1 range:800"]},
        "admin item create":     {"description": "Add a shop item linked to a catalogue entry. Optionally restrict to a business with `business_id`.", "examples": ["/admin item create catalogue_id:1 name:Sword price:500", "/admin item create catalogue_id:3 name:Clone Trooper price:1000 business_id:2"]},
        "admin item edit":       {"description": "Update a shop item's name, price, stock, or business assignment.", "examples": ["/admin item edit item_id:3 price:750"]},
        "admin economy stock-enable": {"description": "Enable public stock trading for a business at a set base price and dividend rate.", "examples": ["/admin economy stock-enable business_id:1 base_price:100 dividend_rate:0.05"]},
        "admin economy exchange-rate": {"description": "Set the exchange rate between two currencies (from → to).", "examples": ["/admin economy exchange-rate from_currency_id:1 to_currency_id:2 rate:1.5"]},
        "admin world bank-create": {"description": "Create a new bank at a location. `range` is optional.", "examples": ["/admin world bank-create name:Central Bank interest_rate:0.02 x:0 y:0"]},
        "admin world bank-edit": {"description": "Edit a bank's name, interest rate, or location.", "examples": ["/admin world bank-edit bank_id:1 interest_rate:0.03"]},
        "admin world travel-speed": {"description": "Set how fast transports travel (units per minute).", "examples": ["/admin world travel-speed speed:10"]},
        "admin world setting":   {"description": "Set an arbitrary server setting key/value.", "examples": ["/admin world setting key:default_currency_id value:1"]},
        # Balance
        "balance":               {"description": "View your current Cash and Bank balances.", "examples": ["/balance"]},
        "pay":                   {"description": "Send currency from your Cash balance to another player.", "examples": ["/pay @User 200"]},
        "deposit":               {"description": "Move currency from your Cash balance into your Bank account.", "examples": ["/deposit 500"]},
        "withdraw":              {"description": "Move currency from your Bank account to your Cash balance.", "examples": ["/withdraw 200"]},
        "leaderboard":           {"description": "Show the top players by Cash balance on this server.", "examples": ["/leaderboard"]},
        # Shop
        "shop":                  {"description": "Browse items available to buy. Only shows items near your location.", "examples": ["/shop", "/shop page:2 sort:Cost"]},
        "buy":                   {"description": "Purchase a shop item by name. You must be near the business that sells it.", "examples": ["/buy Clone Trooper", "/buy Clone Trooper quantity:3"]},
        "sell":                  {"description": "Sell an item or unit from your inventory back to the shop.", "examples": ["/sell DC-15A Blaster Rifle"]},
        "catalogue":             {"description": "View the detailed stats block for a catalogue item.", "examples": ["/catalogue Clone Trooper"]},
        "equip":                 {"description": "Equip an item from your inventory to your character.", "examples": ["/equip Phase I Clone Armor"]},
        "unequip":               {"description": "Unequip an item from your character, returning it to stored inventory.", "examples": ["/unequip Phase I Clone Armor"]},
        "create_unit":           {"description": "Create a named custom unit from a Race in your stored inventory.", "examples": ["/create_unit unit_name:Alpha-1 race_name:Human"]},
        "unassign_equipment":    {"description": "Remove equipment from a unit's slot, returning it to inventory.", "examples": ["/unassign_equipment unit_name:Alpha-1 slot_name:Primary"]},
        # Work
        "work":                  {"description": "Perform work at a nearby business to earn currency. Subject to cooldown.", "examples": ["/work"]},
        # Economy
        "stocks":                {"description": "View your current stock portfolio and the value of each holding.", "examples": ["/stocks"]},
        "buy-stock":             {"description": "Buy shares of a tradeable business at the current market price.", "examples": ["/buy-stock business_id:1 quantity:10"]},
        "pay-dividends":         {"description": "(Admin) Pay out dividends to all shareholders of a business.", "examples": ["/pay-dividends business_id:1"]},
        "loan take":             {"description": "Take a loan from the bank. You must be near the bank. Only one active loan at a time.", "examples": ["/loan take amount:1000"]},
        "loan repay":            {"description": "Make a payment on your outstanding loan. You must be near the bank.", "examples": ["/loan repay amount:500"]},
        "exchange":              {"description": "Exchange one currency for another at the configured exchange rate.", "examples": ["/exchange from_currency_id:1 to_currency_id:2 amount:100"]},
        # Faction
        "faction create":        {"description": "Create a new faction. You become the owner.", "examples": ["/faction create name:Clan Wren description:Mandalorian warriors color:#FF6600"]},
        "faction join":          {"description": "Join an existing faction by name.", "examples": ["/faction join faction_name:Clan Wren"]},
        "faction leave":         {"description": "Leave your current faction. Owners must disband instead.", "examples": ["/faction leave"]},
        "faction info":          {"description": "View a faction's details and member list. Defaults to your own faction.", "examples": ["/faction info", "/faction info faction_name:Clan Wren"]},
        # Logistics
        "garrison assign":       {"description": "Assign one of your units to garrison a named location.", "examples": ["/garrison assign unit_name:Alpha-1 poi_name:Coruscant"]},
        "garrison view":         {"description": "View all units you have garrisoned and their locations.", "examples": ["/garrison view"]},
        "maintenance pay":       {"description": "Pay maintenance costs for all your units.", "examples": ["/maintenance pay"]},
        "transport start":       {"description": "Start transporting a resource between two businesses. You must be near the source.", "examples": ["/transport start from_business_id:1 to_business_id:2 resource_type:Steel quantity:10"]},
        "transport complete":    {"description": "Collect all transports that have arrived at their destination.", "examples": ["/transport complete"]},
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
            value="`/balance` `/pay` `/deposit` `/withdraw` `/leaderboard`",
            inline=False,
        )
        embed.add_field(
            name="🛒 Shop & Inventory",
            value="`/shop` `/buy` `/sell` `/catalogue` `/equip` `/unequip` `/create_unit` `/unassign_equipment`",
            inline=False,
        )
        embed.add_field(
            name="⚒️ Work",
            value="`/work`",
            inline=False,
        )
        embed.add_field(
            name="📈 Economy",
            value="`/stocks` `/buy-stock` `/loan take` `/loan repay` `/exchange`",
            inline=False,
        )
        embed.add_field(
            name="⚔️ Faction",
            value="`/faction create` `/faction join` `/faction leave` `/faction info`",
            inline=False,
        )
        embed.add_field(
            name="🚚 Logistics",
            value="`/garrison assign` `/garrison view` `/maintenance pay` `/transport start` `/transport complete`",
            inline=False,
        )
        embed.add_field(
            name="🔧 Admin",
            value="`/admin setup` `/admin business` `/admin item` `/admin economy` `/admin world`",
            inline=False,
        )

        embed.set_footer(text=f"Use /help <command> for detailed information and examples")
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
