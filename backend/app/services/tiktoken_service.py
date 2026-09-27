"""
TiktokenService — stateless wrapper around the tiktoken library.
Caches Encoding objects per encoding name to avoid repeated BPE model loads.
MUST NOT modify any Tiktoken output.
"""
from __future__ import annotations

import tiktoken

from app.config import SUPPORTED_ENCODINGS
from app.schemas import TokenSchema

# Module-level cache: encoding name → tiktoken.Encoding
_encoding_cache: dict[str, tiktoken.Encoding] = {}


class TiktokenService:
    """Stateless tokenizer service wrapping the tiktoken library."""

    def get_encoding(self, name: str) -> tiktoken.Encoding:
        """Return cached Encoding for *name*, loading it on first access."""
        if name not in _encoding_cache:
            _encoding_cache[name] = tiktoken.get_encoding(name)
        return _encoding_cache[name]

    def tokenize(self, text: str, encoding: str) -> list[TokenSchema]:
        """
        Tokenize *text* with the named encoding.

        Raises ValueError for unsupported encodings.
        Returns one TokenSchema per token; token_text is the UTF-8 decoded bytes
        with <0xXX> hex fallback for non-UTF-8 byte sequences.
        """
        if encoding not in SUPPORTED_ENCODINGS:
            supported = ", ".join(SUPPORTED_ENCODINGS)
            raise ValueError(
                f"Unsupported encoding: '{encoding}'. Supported: {supported}"
            )

        enc = self.get_encoding(encoding)
        token_ids = enc.encode(text)

        tokens: list[TokenSchema] = []
        for idx, token_id in enumerate(token_ids):
            raw_bytes = enc.decode_single_token_bytes(token_id)
            try:
                token_text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                # Represent non-UTF-8 bytes as <0xXX> escape sequences
                token_text = "".join(f"<0x{b:02X}>" for b in raw_bytes)
            tokens.append(TokenSchema(index=idx, token_id=token_id, token_text=token_text))

        return tokens


# Module-level singleton — owned by main.py at startup
tiktoken_service = TiktokenService()
