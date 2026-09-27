"""
Statistics calculation — pure functions, no state.
All functions are safe to call with zero values.
"""


def char_count(text: str) -> int:
    """Return character count of text."""
    return len(text)


def word_count(text: str) -> int:
    """Return word count using whitespace splitting."""
    return len(text.split())


def tokens_per_word(token_count: int, wc: int) -> float:
    """Return tokens per word, rounded to 4 decimal places. Returns 0.0 if no words."""
    if wc == 0:
        return 0.0
    return round(token_count / wc, 4)


def tokens_per_char(token_count: int, cc: int) -> float:
    """Return tokens per character, rounded to 4 decimal places. Returns 0.0 if no chars."""
    if cc == 0:
        return 0.0
    return round(token_count / cc, 4)
