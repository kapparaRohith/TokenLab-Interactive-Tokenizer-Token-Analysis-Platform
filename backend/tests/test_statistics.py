"""
Tests for statistics.py — pure functions, no external dependencies.
"""
from app.services.statistics import char_count, tokens_per_char, tokens_per_word, word_count


class TestCharCount:
    def test_normal(self):
        assert char_count("Hello world!") == 12

    def test_empty(self):
        assert char_count("") == 0

    def test_single_char(self):
        assert char_count("a") == 1

    def test_whitespace(self):
        assert char_count("   ") == 3


class TestWordCount:
    def test_normal(self):
        assert word_count("Hello world") == 2

    def test_empty(self):
        assert word_count("") == 0

    def test_single_word(self):
        assert word_count("hello") == 1

    def test_extra_spaces(self):
        assert word_count("  hello   world  ") == 2


class TestTokensPerWord:
    def test_normal(self):
        result = tokens_per_word(6, 2)
        assert result == 3.0

    def test_zero_words(self):
        assert tokens_per_word(5, 0) == 0.0

    def test_rounds_to_4dp(self):
        result = tokens_per_word(1, 3)
        assert result == round(1 / 3, 4)

    def test_zero_tokens(self):
        assert tokens_per_word(0, 5) == 0.0


class TestTokensPerChar:
    def test_normal(self):
        result = tokens_per_char(3, 12)
        assert result == round(3 / 12, 4)

    def test_zero_chars(self):
        assert tokens_per_char(5, 0) == 0.0

    def test_rounds_to_4dp(self):
        result = tokens_per_char(1, 7)
        assert result == round(1 / 7, 4)

    def test_zero_tokens(self):
        assert tokens_per_char(0, 10) == 0.0
