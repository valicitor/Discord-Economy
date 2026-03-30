from dataclasses import dataclass

@dataclass
class DiscordUser:
    user_id: int
    name: str
    display_avatar: str