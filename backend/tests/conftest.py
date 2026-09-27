"""
Shared pytest fixtures for backend tests.
"""
from __future__ import annotations

import io
import struct

import fitz
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.custom_tokenizer_service import custom_tokenizer_service


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_custom_vocab():
    """Reset custom tokenizer vocabulary before every test to avoid state bleed."""
    custom_tokenizer_service.reset()
    yield
    custom_tokenizer_service.reset()


@pytest.fixture()
def sample_txt_bytes() -> bytes:
    return b"Hello world sample text"


@pytest.fixture()
def sample_pdf_bytes() -> bytes:
    """Create a minimal in-memory text-based PDF using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello from PDF")
    buf = doc.tobytes()
    doc.close()
    return buf


@pytest.fixture()
def empty_pdf_bytes() -> bytes:
    """Create a minimal PDF with no text content (image-only style)."""
    doc = fitz.open()
    doc.new_page()  # empty page, no text
    buf = doc.tobytes()
    doc.close()
    return buf


@pytest.fixture()
def corrupt_pdf_bytes() -> bytes:
    """Bytes that look like a PDF but are corrupted."""
    return b"%PDF-1.4\nCorrupted garbage content\x00\xff"
