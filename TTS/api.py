def synthesize(text: str) -> str:
    """
    Wandelt Text in Sprache um.

    Args:
        text (str): Eingabetext.

    Returns:
        str: Pfad zur Audiodatei.
    """
    try:
        return tts_model.speak(text)
    except Exception as e:
        print(f"Fehler bei der Synthese: {e}")
        return ""
