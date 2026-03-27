def currency_symbol(emoji:str|None, symbol:str|None) -> str:
    """Work out if we should use the emoji or symbol for currency"""

    return(
        emoji.strip()
        if isinstance(emoji, str) and emoji.strip()
        else symbol or ""
    )