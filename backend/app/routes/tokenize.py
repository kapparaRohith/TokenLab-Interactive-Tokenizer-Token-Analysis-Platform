"""
Tokenize routes — thin controllers.
All business logic lives in service classes.
Routes only: validate inputs, dispatch to services, assemble responses.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from app.config import SUPPORTED_ENCODINGS
from app.schemas import (
    EncodingsResponseSchema,
    ResetResponseSchema,
    SourceType,
    TokenizationResultSchema,
    TokenizerMode,
)
from app.services import statistics as stats
from app.services.custom_tokenizer_service import CustomTokenizerService
from app.services.file_processor import FileProcessor, FileValidationError
from app.services.tiktoken_service import TiktokenService

router = APIRouter(prefix="/tokenize", tags=["tokenize"])


# ---------------------------------------------------------------------------
# Dependency providers — singletons injected from main.py at import time
# ---------------------------------------------------------------------------

def get_tiktoken_service() -> TiktokenService:  # noqa: D401
    from app.services.tiktoken_service import tiktoken_service
    return tiktoken_service


def get_custom_service() -> CustomTokenizerService:  # noqa: D401
    from app.services.custom_tokenizer_service import custom_tokenizer_service
    return custom_tokenizer_service


def get_file_processor() -> FileProcessor:  # noqa: D401
    from app.services.file_processor import file_processor
    return file_processor


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/encodings", response_model=EncodingsResponseSchema)
async def list_encodings() -> EncodingsResponseSchema:
    """Return the list of supported Tiktoken encoding names."""
    return EncodingsResponseSchema(encodings=SUPPORTED_ENCODINGS)


@router.post("/text", response_model=TokenizationResultSchema)
async def tokenize_text(
    text: str = Form(...),
    tokenizer: str = Form(...),
    encoding: str | None = Form(None),
    tiktoken_svc: TiktokenService = Depends(get_tiktoken_service),
    custom_svc: CustomTokenizerService = Depends(get_custom_service),
) -> TokenizationResultSchema:
    """Tokenize a plain text string using Tiktoken or Custom Tokenizer."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    if tokenizer == TokenizerMode.tiktoken:
        if not encoding:
            raise HTTPException(
                status_code=400, detail="Encoding is required for Tiktoken mode."
            )
        try:
            tokens = tiktoken_svc.tokenize(text, encoding)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return _build_result(
            original_text=text,
            source_type=SourceType.text,
            tokenizer=TokenizerMode.tiktoken,
            encoding=encoding,
            tokens=tokens,
            vocabulary=None,
            new_token_ids=None,
        )

    elif tokenizer == TokenizerMode.custom:
        tokens, vocabulary, new_token_ids = custom_svc.tokenize(text)
        return _build_result(
            original_text=text,
            source_type=SourceType.text,
            tokenizer=TokenizerMode.custom,
            encoding="custom",
            tokens=tokens,
            vocabulary=vocabulary,
            new_token_ids=new_token_ids,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tokenizer mode: '{tokenizer}'. Use 'tiktoken' or 'custom'.",
        )


@router.post("/file", response_model=TokenizationResultSchema)
async def tokenize_file(
    file: UploadFile,
    tokenizer: str = Form(...),
    encoding: str | None = Form(None),
    tiktoken_svc: TiktokenService = Depends(get_tiktoken_service),
    custom_svc: CustomTokenizerService = Depends(get_custom_service),
    fp: FileProcessor = Depends(get_file_processor),
) -> TokenizationResultSchema:
    """Upload a TXT or PDF file, extract text, and tokenize it."""
    file_bytes = await file.read()

    try:
        extracted_text, source_type = fp.extract_text(
            file_bytes, file.filename or "", file.content_type or ""
        )
    except FileValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    if tokenizer == TokenizerMode.tiktoken:
        if not encoding:
            raise HTTPException(
                status_code=400, detail="Encoding is required for Tiktoken mode."
            )
        try:
            tokens = tiktoken_svc.tokenize(extracted_text, encoding)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return _build_result(
            original_text=extracted_text,
            source_type=source_type,
            tokenizer=TokenizerMode.tiktoken,
            encoding=encoding,
            tokens=tokens,
            vocabulary=None,
            new_token_ids=None,
        )

    elif tokenizer == TokenizerMode.custom:
        tokens, vocabulary, new_token_ids = custom_svc.tokenize(extracted_text)
        return _build_result(
            original_text=extracted_text,
            source_type=source_type,
            tokenizer=TokenizerMode.custom,
            encoding="custom",
            tokens=tokens,
            vocabulary=vocabulary,
            new_token_ids=new_token_ids,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tokenizer mode: '{tokenizer}'. Use 'tiktoken' or 'custom'.",
        )


@router.post("/custom/reset", response_model=ResetResponseSchema)
async def reset_custom_vocabulary(
    custom_svc: CustomTokenizerService = Depends(get_custom_service),
) -> ResetResponseSchema:
    """Reset the Custom Tokenizer vocabulary to empty state."""
    custom_svc.reset()
    return ResetResponseSchema(message="Custom tokenizer vocabulary has been reset.")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_result(
    *,
    original_text: str,
    source_type: SourceType,
    tokenizer: TokenizerMode,
    encoding: str,
    tokens: list,
    vocabulary: list | None,
    new_token_ids: list[int] | None,
) -> TokenizationResultSchema:
    """Assemble the final TokenizationResultSchema from components."""
    cc = stats.char_count(original_text)
    wc = stats.word_count(original_text)
    tc = len(tokens)
    return TokenizationResultSchema(
        original_text=original_text,
        source_type=source_type,
        tokenizer=tokenizer,
        encoding=encoding,
        token_count=tc,
        tokens=tokens,
        token_ids=[t.token_id for t in tokens],
        token_texts=[t.token_text for t in tokens],
        char_count=cc,
        word_count=wc,
        tokens_per_word=stats.tokens_per_word(tc, wc),
        tokens_per_char=stats.tokens_per_char(tc, cc),
        vocabulary=vocabulary,
        new_token_ids=new_token_ids,
    )
