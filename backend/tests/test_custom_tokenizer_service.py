"""
Tests for CustomTokenizerService.
SC-003: determinism guarantee — same input → identical token ID sequences.
"""
import pytest

from app.services.custom_tokenizer_service import CustomTokenizerService


@pytest.fixture()
def svc() -> CustomTokenizerService:
    """Fresh service instance per test (not the module singleton)."""
    return CustomTokenizerService()


class TestCustomTokenizerService:
    def test_hello_world_produces_expected_tokens(self, svc):
        tokens, _, _ = svc.tokenize("Hello world!")
        texts = [t.token_text for t in tokens]
        assert "Hello" in texts or any("Hello" in t for t in texts)

    def test_token_indices_are_sequential(self, svc):
        tokens, _, _ = svc.tokenize("Hello world!")
        for i, t in enumerate(tokens):
            assert t.index == i

    def test_sc003_determinism(self, svc):
        """Same input twice must produce identical token ID sequences."""
        tokens1, _, _ = svc.tokenize("Hello world!")
        tokens2, _, _ = svc.tokenize("Hello world!")
        assert [t.token_id for t in tokens1] == [t.token_id for t in tokens2]

    def test_first_call_marks_all_new(self, svc):
        _, vocab, new_ids = svc.tokenize("Hello world!")
        assert all(e.is_new for e in vocab)
        assert len(new_ids) > 0

    def test_second_call_marks_existing(self, svc):
        svc.tokenize("Hello world!")
        _, vocab, new_ids = svc.tokenize("Hello world!")
        assert all(not e.is_new for e in vocab)
        assert new_ids == []

    def test_frequency_increments_on_second_call(self, svc):
        svc.tokenize("Hello world!")
        _, vocab, _ = svc.tokenize("Hello world!")
        assert all(e.frequency == 2 for e in vocab)

    def test_reset_clears_vocabulary(self, svc):
        svc.tokenize("Hello world!")
        svc.reset()
        assert svc.get_vocabulary() == []

    def test_reset_resets_id_counter(self, svc):
        svc.tokenize("Hello world!")
        svc.reset()
        _, vocab, _ = svc.tokenize("Hi")
        assert vocab[0].token_id == 0

    def test_after_reset_tokens_are_new_again(self, svc):
        svc.tokenize("Hello world!")
        svc.reset()
        _, vocab, new_ids = svc.tokenize("Hello world!")
        assert all(e.is_new for e in vocab)
        assert len(new_ids) > 0

    def test_mixed_new_and_existing(self, svc):
        svc.tokenize("Hello")
        tokens, vocab, new_ids = svc.tokenize("Hello world")
        hello_entry = next(e for e in vocab if "Hello" in e.token_text)
        world_entry = next(e for e in vocab if "world" in e.token_text or " world" in e.token_text)
        assert not hello_entry.is_new
        assert world_entry.is_new

    def test_token_ids_are_unique_and_dense(self, svc):
        _, vocab, _ = svc.tokenize("Hello world foo bar")
        ids = [e.token_id for e in vocab]
        assert ids == list(range(len(ids)))

    def test_token_text_is_uniqueness_key(self, svc):
        svc.tokenize("Hello Hello Hello")
        vocab = svc.get_vocabulary()
        hello_entries = [e for e in vocab if e.token_text == " Hello"]
        # Only one entry for " Hello" regardless of how many times it appears
        assert len(hello_entries) == 1
        assert hello_entries[0].frequency == 2

    def test_vocabulary_sorted_by_token_id(self, svc):
        _, vocab, _ = svc.tokenize("foo bar baz")
        ids = [e.token_id for e in vocab]
        assert ids == sorted(ids)
