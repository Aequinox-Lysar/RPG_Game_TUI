def sanitize_emoji(text: str) -> str:
    """
    Entfernt unsichtbare Unicode-Variation-Selectoren (z. B. U+FE0F),
    die bei Emojis oft Darstellungsprobleme verursachen.
    """
    return text.replace("\ufe0f", "")
