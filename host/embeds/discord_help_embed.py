import discord
from config import BOT_NAME, BOT_VERSION

class DiscordHelpEmbed:
    COMMAND_INFO = {

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
            title=f"🤖 {BOT_NAME} bot v{BOT_VERSION} - Help Menu",
            description="Advanced submission review system with category-based evaluation",
            color=discord.Color.blue()
        )
    
        # Admin Commands
        embed.add_field(
            name="📝 Admin Commands",
            value=f"""
                    """,
            inline=False
        )
    
        embed.set_footer(text=f"Use /help <command> for detailed command information")
    
        return embed

    @staticmethod
    def command_help(command_name):
        info = DiscordHelpEmbed.COMMAND_INFO.get(command_name, {})

        embed = discord.Embed(
            title=f"ℹ️ Command: /{command_name}",
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
    def version_embed():
        embed = discord.Embed(
            title=f"🤖 {BOT_NAME} bot Version",
            description=f"Current {BOT_NAME} bot version: v{BOT_VERSION}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Thank you for using {BOT_NAME} Bot!")
        return embed

    @staticmethod
    def command_faq():
        embed = discord.Embed(
            title=f"🤖 {BOT_NAME} bot v{BOT_VERSION} - FAQs",
            description="Common questions about the bot",
            color=discord.Color.blue()
        )

        # embed.add_field(
        #     name="❓ How do I verify a submission?",
        #     value=f"Use the `/verify_content <verification_token> <text_or_link>` command. Example: `/verify_content \"abc123\" \"A powerful fireball ability\"`",
        #     inline=False
        # )

        embed.set_footer(text=f"Use /help <command> for detailed command information")
    
        return embed