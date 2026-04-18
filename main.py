import discord
from discord import app_commands
from discord.ext import commands
from config import BOT_NAME, BOT_VERSION, DISCORD_BOT_TOKEN, TEST_SERVER_ID, DO_GLOBAL_SYNC, FORCE_SYNC
import asyncio
from infrastructure import BaseRepository

# ----------------------------
# Command sync Class
# ----------------------------
class CommandSyncManager:
    def __init__(self, tree: discord.app_commands.CommandTree):
        self.tree = tree

    async def sync_if_needed(self):
        test_guild = discord.Object(id=TEST_SERVER_ID)

        local_commands = self.tree.get_commands()
        if not local_commands:
            print("No local commands found. Skipping sync.")
            return

        remote_commands = await self.tree.fetch_commands(guild=test_guild)

        if not remote_commands:
            print("No commands registered. Performing initial sync.")
            self.tree.copy_global_to(guild=test_guild)
            synced = await self.tree.sync(guild=test_guild)
            print(f"✅ Synced {len(synced)} commands")
            return

        print(f"Found {len(remote_commands)} commands registered.")

        if FORCE_SYNC or self.commands_are_different(remote_commands, local_commands):
            print("Commands changed. Syncing...")
            self.tree.copy_global_to(guild=test_guild)
            synced = await self.tree.sync(guild=test_guild)
            print(f"✅ Synced {len(synced)} commands")
        else:
            print("Commands identical. Skipping sync.")
    
    async def sync_global_if_needed(self):
        local_commands = self.tree.get_commands()

        if not local_commands:
            print("No local global commands found. Skipping sync.")
            return

        remote_commands = await self.tree.fetch_commands()

        if not remote_commands:
            print("No global commands registered. Performing initial sync.")
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} global commands")
            return

        print(f"Found {len(remote_commands)} global commands registered.")

        if FORCE_SYNC or self.commands_are_different(remote_commands, local_commands):
            print("Global commands changed. Syncing...")
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} global commands")
        else:
            print("Global commands identical. Skipping sync.")

    # -------------------------
    # Comparison Logic
    # -------------------------

    def normalize_local_command(self, cmd):
        return (
            cmd.name,
            cmd.description,
        )

    def normalize_remote_command(self, cmd):
        return (
            cmd.name,
            cmd.description,
        )

    def commands_are_different(self, remote, local):
        remote_norm = sorted(self.normalize_remote_command(c) for c in remote)
        local_norm = sorted(self.normalize_local_command(c) for c in local)
        return remote_norm != local_norm

# ----------------------------
# Bot Class
# ----------------------------
class MyClient(commands.Bot):
    BOT_ROLE = "dev"
    COG_MAP = {
        "dev"  : [
            "host.cogs.admin",
            "host.cogs.balance",
            "host.cogs.work",
            "host.cogs.units",
        ],
        # "merchant": [
        #     "host.cogs.balance",
        #     "host.cogs.shop",
        #     "host.cogs.inventory",
        # ],
        # "commander": [
        #     "host.cogs.units",
        #     "host.cogs.equipment",
        #     "host.cogs.travel",
        #     "host.cogs.poi",
        # ],
        # "government": [
        #     "host.cogs.admin",
        # ],
        # "workforce": [
        #     "host.cogs.actions",
        #     "host.cogs.robbery",
        # ]
    }
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # If you need message content
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Load cogs asynchronously if using commands.Bot extensions
        cog_tasks = self._load_all_cogs()

        await asyncio.gather(cog_tasks)
        print("✅ All cogs loaded.")
    
    async def _load_all_cogs(self):
        cogs = self.COG_MAP.get(self.BOT_ROLE, [])

        async def load_cog(cog):
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded cog: {cog}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog}: {e}")

        # Run cog loads concurrently
        await asyncio.gather(*(load_cog(cog) for cog in cogs))

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'{BOT_NAME} bot v{BOT_VERSION} is ready!')
        print(f'Connected to {len(self.guilds)} guilds: {[guild.name for guild in self.guilds]}')

        # Check if TEST_SERVER_ID exists in config and sync commands if so
        if TEST_SERVER_ID != None:
            sync_manager = CommandSyncManager(self.tree)
            await sync_manager.sync_if_needed()

        # Only sync globally when explicitly enabled
        if DO_GLOBAL_SYNC:
            await sync_manager.sync_global_if_needed()
        
        print("✅ Bot is fully ready and synced.")


    async def on_interaction(self, interaction: discord.Interaction):
        # Log all interactions
        print(f"Command received: {interaction.command} from {interaction.user} "
              f"in {interaction.guild.name if interaction.guild else 'DM'}")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        print(f"❌ Error: Command error from {interaction.user}: {error}")

        if isinstance(error, app_commands.MissingRequiredArgument):
            await interaction.response.send_message(
                "❌ Please provide all required arguments. Use `/help` for guidance.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.CommandNotFound):
            pass  # ignore unknown commands
        else:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(error)}",
                ephemeral=True
            )
            print(f"❌ Error: Unexpected command error: {error}")

# ----------------------------
# Async Main Function
# ----------------------------
async def main():
    if not DISCORD_BOT_TOKEN:
        print("❌ Error: DISCORD_BOT_TOKEN not set in configuration!")
        return

    client = MyClient()
    print(f"Starting {BOT_NAME} bot v{BOT_VERSION}...")

    try:
        await client.start(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        # Ctrl+C pressed
        print("KeyboardInterrupt received. Shutting down...")
        await client.close()
        await BaseRepository.close_all()
    except asyncio.CancelledError:
        # Suppress cancellation traceback on shutdown
        pass
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if not client.is_closed():
            await client.close()
            await BaseRepository.close_all()
        print("Bot has shut down gracefully.")

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    asyncio.run(main())
