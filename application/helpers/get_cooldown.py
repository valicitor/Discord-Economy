from datetime import datetime, timezone

def get_countdown(remaining_seconds: int) -> int:

    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60

    formatted_hours = f"{hours}h" if hours > 0 else ""
    formatted_minutes = f"{minutes}m" if minutes > 0 else ""
    formatted_seconds = f"{seconds}s" if seconds > 0 else ""
    countdown = f"{formatted_hours}{formatted_minutes}{formatted_seconds}"

    return countdown