"""
FileProcessor — stateless file validation and text extraction service.

Raises plain Python exceptions (NOT HTTPException) — route handlers are
responsible for converting these to HTTP error responses. This keeps HTTP
concerns out of the service layer (Constitution Principle V).
"""
from __future__ import annotations

import fitz  # PyMuPDF

from app.config import MAX_UPLOAD_BYTES
from app.schemas import SourceType


class FileValidationError(Exception):
    """Raised for invalid input files (wrong type, empty, corrupt)."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class FileProcessor:
    """Stateless file validation and text extraction."""

    ALLOWED_TXT_EXTENSIONS = {".txt"}
    ALLOWED_PDF_EXTENSIONS = {".pdf"}

    @staticmethod
    def extract_text(
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> tuple[str, SourceType]:
        """
        Validate and extract text from an uploaded file.

        Args:
            file_bytes: raw file content
            filename: original filename (used for extension check)
            content_type: MIME type reported by the client

        Returns:
            (extracted_text, source_type) tuple

        Raises:
            FileValidationError: for any validation or extraction failure
        """
        lower_name = (filename or "").lower()
        is_txt = lower_name.endswith(".txt") or content_type in (
            "text/plain",
            "text/txt",
        )
        is_pdf = lower_name.endswith(".pdf") or content_type == "application/pdf"

        if not is_txt and not is_pdf:
            raise FileValidationError(
                "Unsupported file type. Only .txt and .pdf files are accepted."
            )

        if len(file_bytes) > MAX_UPLOAD_BYTES:
            raise FileValidationError(
                "File too large. Maximum allowed size is 10 MB.", status_code=413
            )

        if is_txt:
            return FileProcessor._extract_txt(file_bytes)
        return FileProcessor._extract_pdf(file_bytes)

    @staticmethod
    def _extract_txt(file_bytes: bytes) -> tuple[str, SourceType]:
        text = file_bytes.decode("utf-8", errors="replace").strip()
        if not text:
            raise FileValidationError("The uploaded file contains no text content.")
        return text, SourceType.txt

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> tuple[str, SourceType]:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except fitz.FileDataError:
            raise FileValidationError("PDF is corrupted or unreadable.")
        except Exception:
            raise FileValidationError("PDF is corrupted or unreadable.")

        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()

        text = "".join(pages_text).strip()
        if not text:
            raise FileValidationError(
                "No extractable text found in PDF. The file may contain only images or scanned content."
            )
        return text, SourceType.pdf


# Module-level singleton (stateless — shared instance is safe)
file_processor = FileProcessor()
