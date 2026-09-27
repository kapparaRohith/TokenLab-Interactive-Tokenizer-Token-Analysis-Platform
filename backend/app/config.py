"""
Application configuration.
All values can be overridden via environment variables.
"""
import os

# Maximum allowed upload size in bytes (default: 10 MB)
MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))

# Supported Tiktoken encodings (fixed list — not user-configurable)
SUPPORTED_ENCODINGS: list[str] = [
    "cl100k_base",
    "p50k_base",
    "p50k_edit",
    "r50k_base",
    "o200k_base",
]
