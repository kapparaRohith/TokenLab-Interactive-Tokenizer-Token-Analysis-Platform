"""
Pydantic schemas for all request/response models.
These are the single source of truth for API contracts.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class TokenizerMode(str, Enum):
    tiktoken = "tiktoken"
    custom = "custom"


class SourceType(str, Enum):
    text = "text"
    txt = "txt"
    pdf = "pdf"


class TokenSchema(BaseModel):
    index: int
    token_id: int
    token_text: str


class VocabularyEntrySchema(BaseModel):
    token_id: int
    token_text: str
    frequency: int
    is_new: bool


class TokenizationResultSchema(BaseModel):
    original_text: str
    source_type: SourceType
    tokenizer: TokenizerMode
    encoding: str
    token_count: int
    tokens: list[TokenSchema]
    token_ids: list[int]
    token_texts: list[str]
    char_count: int
    word_count: int
    tokens_per_word: float
    tokens_per_char: float
    vocabulary: list[VocabularyEntrySchema] | None = None
    new_token_ids: list[int] | None = None


class EncodingsResponseSchema(BaseModel):
    encodings: list[str]


class ResetResponseSchema(BaseModel):
    message: str


class HealthResponseSchema(BaseModel):
    status: str
