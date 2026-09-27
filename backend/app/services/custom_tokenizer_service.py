"""
CustomTokenizerService — regex-based tokenizer with in-memory vocabulary.

Architecture:
- Internal state: plain dict keyed by token_text → entry dataclass (NOT Pydantic model)
- Pydantic models are constructed only at response serialization time
- Singleton is owned by main.py and injected into routes; never instantiated in services layer
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas import TokenSchema, VocabularyEntrySchema

# Compiled regex pattern — deterministic token splitting strategy.
# Priority order: contractions → words (with optional leading space) → digits → punctuation
PATTERN = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d|\s*[a-zA-Z]+|\d+|[^\s\w]")


@dataclass
class _VocabEntry:
    """Internal mutable vocabulary record. NOT a Pydantic model."""

    token_id: int
    token_text: str
    frequency: int = 0
    is_new: bool = False


class CustomTokenizerService:
    """
    Stateful tokenizer service with in-memory vocabulary.

    Singleton instance must be created once in main.py and injected via FastAPI Depends.
    Call reset() between test runs to clear vocabulary state.
    """

    def __init__(self) -> None:
        self._vocab: dict[str, _VocabEntry] = {}
        self._next_id: int = 0

    def tokenize(
        self, text: str
    ) -> tuple[list[TokenSchema], list[VocabularyEntrySchema], list[int]]:
        """
        Tokenize *text* using the regex pattern.

        Returns:
            tokens: ordered list of TokenSchema (index, token_id, token_text)
            vocabulary: snapshot of full vocabulary sorted by token_id
            new_token_ids: IDs of tokens newly created during this call
        """
        raw_tokens = re.findall(PATTERN, text)
        new_token_ids: list[int] = []

        # Reset is_new flag for all existing entries before this call
        for entry in self._vocab.values():
            entry.is_new = False

        token_schemas: list[TokenSchema] = []
        for idx, token_text in enumerate(raw_tokens):
            if token_text in self._vocab:
                entry = self._vocab[token_text]
                entry.frequency += 1
                # is_new already reset to False above
            else:
                entry = _VocabEntry(
                    token_id=self._next_id,
                    token_text=token_text,
                    frequency=1,
                    is_new=True,
                )
                self._vocab[token_text] = entry
                new_token_ids.append(self._next_id)
                self._next_id += 1

            token_schemas.append(
                TokenSchema(index=idx, token_id=entry.token_id, token_text=token_text)
            )

        vocabulary_snapshot = self._build_vocabulary_snapshot()
        return token_schemas, vocabulary_snapshot, new_token_ids

    def reset(self) -> None:
        """Clear vocabulary and reset the ID counter."""
        self._vocab = {}
        self._next_id = 0

    def get_vocabulary(self) -> list[VocabularyEntrySchema]:
        """Return current vocabulary sorted by token_id."""
        return self._build_vocabulary_snapshot()

    def _build_vocabulary_snapshot(self) -> list[VocabularyEntrySchema]:
        """Build a sorted Pydantic snapshot of current vocabulary state."""
        return [
            VocabularyEntrySchema(
                token_id=e.token_id,
                token_text=e.token_text,
                frequency=e.frequency,
                is_new=e.is_new,
            )
            for e in sorted(self._vocab.values(), key=lambda x: x.token_id)
        ]


# Module-level singleton — owned by main.py
custom_tokenizer_service = CustomTokenizerService()
