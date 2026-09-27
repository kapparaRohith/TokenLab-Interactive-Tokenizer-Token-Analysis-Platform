"""
Tests for FileProcessor.
Tests both TXT and PDF extraction paths, and all error scenarios.
"""
import pytest

from app.services.file_processor import FileProcessor, FileValidationError
from app.schemas import SourceType


@pytest.fixture()
def fp() -> FileProcessor:
    return FileProcessor()


class TestTxtExtraction:
    def test_valid_utf8_txt(self, fp):
        text, source = fp.extract_text(b"Hello world", "test.txt", "text/plain")
        assert text == "Hello world"
        assert source == SourceType.txt

    def test_strips_whitespace(self, fp):
        text, _ = fp.extract_text(b"  hello  \n", "test.txt", "text/plain")
        assert text == "hello"

    def test_whitespace_only_raises(self, fp):
        with pytest.raises(FileValidationError, match="no text content"):
            fp.extract_text(b"   \n\t", "test.txt", "text/plain")

    def test_empty_raises(self, fp):
        with pytest.raises(FileValidationError, match="no text content"):
            fp.extract_text(b"", "test.txt", "text/plain")

    def test_latin1_chars_do_not_crash(self, fp):
        # Latin-1 bytes that are not valid UTF-8
        latin1_bytes = "café".encode("latin-1")
        text, _ = fp.extract_text(latin1_bytes, "test.txt", "text/plain")
        assert isinstance(text, str)

    def test_txt_detected_by_content_type(self, fp):
        text, source = fp.extract_text(b"Hello", "noextension", "text/plain")
        assert source == SourceType.txt


class TestPdfExtraction:
    def test_valid_pdf(self, fp, sample_pdf_bytes):
        text, source = fp.extract_text(sample_pdf_bytes, "test.pdf", "application/pdf")
        assert "Hello from PDF" in text
        assert source == SourceType.pdf

    def test_empty_pdf_raises(self, fp, empty_pdf_bytes):
        with pytest.raises(FileValidationError, match="No extractable text"):
            fp.extract_text(empty_pdf_bytes, "test.pdf", "application/pdf")

    def test_corrupt_pdf_raises(self, fp, corrupt_pdf_bytes):
        with pytest.raises(FileValidationError, match="corrupted"):
            fp.extract_text(corrupt_pdf_bytes, "test.pdf", "application/pdf")

    def test_pdf_detected_by_content_type(self, fp, sample_pdf_bytes):
        _, source = fp.extract_text(sample_pdf_bytes, "noextension", "application/pdf")
        assert source == SourceType.pdf


class TestValidation:
    def test_unsupported_type_raises(self, fp):
        with pytest.raises(FileValidationError, match="Unsupported file type"):
            fp.extract_text(b"data", "test.docx", "application/octet-stream")

    def test_oversized_file_raises_413(self, fp):
        big = b"x" * (10 * 1024 * 1024 + 1)
        with pytest.raises(FileValidationError) as exc_info:
            fp.extract_text(big, "test.txt", "text/plain")
        assert exc_info.value.status_code == 413
        assert "10 MB" in str(exc_info.value)
