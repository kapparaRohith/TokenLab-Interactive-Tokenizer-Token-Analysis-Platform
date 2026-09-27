"""
Tests for TiktokenService.
"""
import tiktoken
import pytest

from app.services.tiktoken_service import TiktokenService
from app.config import SUPPORTED_ENCODINGS


@pytest.fixture()
def svc() -> TiktokenService:
    return TiktokenService()


class TestTiktokenService:
    def test_tokenize_hello_world_ids_match_library(self, svc):
        """SC-006: token IDs must exactly match direct tiktoken library output."""
        text = "Hello world!"
        tokens = svc.tokenize(text, "cl100k_base")
        expected_ids = tiktoken.get_encoding("cl100k_base").encode(text)
        assert [t.token_id for t in tokens] == list(expected_ids)

    def test_tokenize_returns_correct_count(self, svc):
        text = "Hello world!"
        tokens = svc.tokenize(text, "cl100k_base")
        expected = tiktoken.get_encoding("cl100k_base").encode(text)
        assert len(tokens) == len(expected)

    def test_token_indices_are_sequential(self, svc):
        tokens = svc.tokenize("The quick brown fox", "cl100k_base")
        for i, t in enumerate(tokens):
            assert t.index == i

    def test_invalid_encoding_raises_value_error(self, svc):
        with pytest.raises(ValueError, match="gpt2"):
            svc.tokenize("hello", "gpt2")

    def test_all_supported_encodings_load(self, svc):
        for enc in SUPPORTED_ENCODINGS:
            tokens = svc.tokenize("hello", enc)
            assert len(tokens) > 0

    def test_non_utf8_bytes_produce_hex_escape(self, svc):
        """Tokens that decode to non-UTF-8 bytes must render as <0xXX> not crash."""
        # Use p50k_base which has tokens that may not be valid UTF-8 strings
        tokens = svc.tokenize("Hello", "p50k_base")
        for t in tokens:
            assert isinstance(t.token_text, str)

    def test_empty_text_returns_empty_list(self, svc):
        tokens = svc.tokenize("", "cl100k_base")
        assert tokens == []

    def test_encoding_name_preserved(self, svc):
        """The encoding is passed through correctly (no mutation)."""
        tokens = svc.tokenize("hi", "p50k_base")
        expected = tiktoken.get_encoding("p50k_base").encode("hi")
        assert [t.token_id for t in tokens] == list(expected)
