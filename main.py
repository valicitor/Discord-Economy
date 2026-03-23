import discord
from discord import app_commands
from discord.ext import commands
from config import BOT_NAME, BOT_VERSION, DISCORD_BOT_TOKEN, TEST_SERVER_ID
import asyncio

# ----------------------------
# Bot Class
# ----------------------------
class MyClient(commands.Bot):
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
        cogs = [
            "host.cogs.admin",
            "host.cogs.help",
            "host.cogs.balance",
        ]

        async def load_cog(cog):
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded cog: {cog}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog}: {e}")

        # Run cog loads concurrently
        await asyncio.gather(*(load_cog(cog) for cog in cogs))
    
    # ----------------------------
    # Delete Commands Concurrently
    # ----------------------------
    async def clear_commands_from_guild(self, guild_id: int):
        print(f"Clearing commands from guild {guild_id}...")
        try:
            guild = discord.Object(id=guild_id)
            commands_list = await self.tree.fetch_commands(guild=guild)
            if not commands_list:
                print(f"No commands to delete in guild {guild_id}")
                return

            async def delete_cmd(cmd):
                try:
                    await cmd.delete()
                    print(f"🗑️ Deleted guild command: {cmd.name}")
                except Exception as e:
                    print(f"❌ Failed to delete {cmd.name} in guild {guild_id}: {e}")

            await asyncio.gather(*(delete_cmd(cmd) for cmd in commands_list))
            print(f"✅ Deleted {len(commands_list)} commands from guild {guild_id}")

        except Exception as e:
            print(f"❌ Failed to clear commands from guild {guild_id}: {e}")

    async def clear_commands_globally(self):
        print("Clearing global commands...")
        try:
            commands_list = await self.tree.fetch_commands()
            if not commands_list:
                print("No global commands to delete.")
                return

            async def delete_cmd(cmd):
                try:
                    await cmd.delete()
                    print(f"🗑️ Deleted global command: {cmd.name}")
                except Exception as e:
                    print(f"❌ Failed to delete global command {cmd.name}: {e}")

            await asyncio.gather(*(delete_cmd(cmd) for cmd in commands_list))
            print(f"✅ Deleted {len(commands_list)} global commands.")
        except Exception as e:
            print(f"❌ Failed to clear global commands: {e}")

    # ----------------------------
    # Sync Commands Concurrently
    # ----------------------------
    async def sync_commands_to_guilds(self, guild_ids: list[int]):
        print(f"Syncing commands to guilds {guild_ids}...")
        semaphore = asyncio.Semaphore(3)  # limit concurrency to avoid rate-limits

        async def sync_guild(guild_id):
            async with semaphore:
                try:
                    guild = discord.Object(id=guild_id)
                    self.tree.copy_global_to(guild=guild)
                    synced = await self.tree.sync(guild=guild)
                    print(f"✅ Synced {len(synced)} commands to guild {guild_id}")
                except Exception as e:
                    print(f"❌ Failed to sync guild {guild_id}: {e}")

        try:
            await asyncio.gather(*(sync_guild(gid) for gid in guild_ids))
            print("✅ All guild syncs completed.")
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"Rate-limited: {e}")
            else:
                print(f"HTTPException: {e}")

    async def sync_commands_globally(self):
        print("Syncing global commands...")
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} global commands.")
        except Exception as e:
            print(f"❌ Failed to sync global commands: {e}")

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'{BOT_NAME} bot v{BOT_VERSION} is ready!')
        print(f'Connected to {len(self.guilds)} guilds: {[guild.name for guild in self.guilds]}')

        # Clear and sync commands as needed
        # Test server commands
        await self.clear_commands_from_guild(TEST_SERVER_ID)
        await self.sync_commands_to_guilds([TEST_SERVER_ID])

        # Global commands
        # await self.clear_commands_globally()
        # await self.sync_commands_globally()


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
    except asyncio.CancelledError:
        # Suppress cancellation traceback on shutdown
        pass
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("Bot has shut down gracefully.")

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    asyncio.run(main())