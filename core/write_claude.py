def claude_write_full_script(fact_spine: dict, tone_preset: str, min_words: int, max_words: int) -> str:
    # TODO: Replace with Anthropic API call
    return (
        "COLD OPEN\n"
        "Pay attention to this photograph...\n\n"
        f"[STUB SCRIPT — tone={tone_preset}, target={min_words}-{max_words} words]\n"
    )
