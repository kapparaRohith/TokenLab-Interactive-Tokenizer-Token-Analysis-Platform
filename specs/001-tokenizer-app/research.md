# Research Notes: Tokenizer Application

**Feature**: 001-tokenizer-app
**Date**: 2026-09-27
**Phase**: 0 — Outline & Research

---

## Decision Log

### D-001: Frontend Framework — React + TypeScript

**Decision**: React 18 with TypeScript (strict mode).
**Rationale**: Specified by user. TypeScript adds compile-time safety for API response
shapes and component props, reducing runtime surprises. Vite is the build tool of choice
for its fast dev server and minimal configuration overhead.
**Alternatives considered**: Next.js (rejected — no SSR needed, adds unnecessary
complexity), CRA (rejected — deprecated).

---

### D-002: Backend Framework — FastAPI + Python

**Decision**: FastAPI with Python 3.11+, Uvicorn as ASGI server.
**Rationale**: Specified by user. FastAPI's Pydantic-native request/response model
guarantees schema enforcement at the boundary without manual validation code. Async
support allows non-blocking I/O for file reads.
**Alternatives considered**: Flask (rejected — no native schema validation), Django
(rejected — too much infrastructure for a stateless API).

---

### D-003: Tiktoken Integration

**Decision**: Use the `tiktoken` Python library directly. Wrap it in a
`TiktokenService` class. Treat Tiktoken as a read-only, externally authoritative
dependency. Supported encodings: `cl100k_base`, `p50k_base`, `p50k_edit`, `r50k_base`,
`o200k_base`. This list is fixed at implementation time from available Tiktoken encodings.
**Rationale**: Tiktoken is the canonical tokenizer for OpenAI models. Must not be
modified. Each encoding is fetched via `tiktoken.get_encoding(name)`.
**Decoding strategy**: `enc.decode_single_token_bytes(token_id)` per token. If bytes
are not valid UTF-8, fall back to the hex-escaped representation (e.g., `<0x0A>`).
**Alternatives considered**: HuggingFace tokenizers (rejected — different library,
out of scope).

---

### D-004: Custom Tokenizer Algorithm — Regex-based Splitting

**Decision**: Use Python `re` module with a deterministic regex pattern to split text
into tokens. Pattern priority order (applied left-to-right via `re.findall`):
1. Contractions: `'s|'t|'re|'ve|'m|'ll|'d` (apostrophe variants)
2. Words with optional leading space: `\s*[a-zA-Z]+`
3. Numbers: `\d+`
4. Punctuation and symbols: `[^\s\w]`

This mirrors the spirit of the GPT-2 tokenizer regex without depending on Tiktoken.
Determinism guarantee: same regex on same input always produces the same token sequence.
**Rationale**: Regex splitting is simple, dependency-free, deterministic, and clearly
testable. Using `re.findall` with a compiled pattern is efficient for the text sizes
this application targets.
**Alternatives considered**: Whitespace-only split (rejected — loses punctuation
granularity), full BPE (rejected — requires training data, out of scope).

---

### D-005: Custom Vocabulary State & Lifecycle

**Decision**: The `CustomTokenizerService` holds an in-memory `dict[str, VocabularyEntry]`
keyed by token text. A monotonically incrementing integer counter provides the next
available token ID. The service is instantiated once at application startup and lives
for the FastAPI process lifetime.
**ID assignment**: IDs start at 0. Each new unique token text receives
`next_id` and `next_id` increments. The same token text always maps to the same ID
within a session — this is guaranteed by the dict key uniqueness.
**Frequency tracking**: Each `VocabularyEntry` holds a `frequency: int` field
incremented on every occurrence across all tokenization calls.
**Reset**: A dedicated `reset()` method clears the dict and resets the counter to 0.
FastAPI exposes this as `POST /tokenize/custom/reset`.
**Alternatives considered**: Redis (rejected — no persistence required, adds
infrastructure), file-based persistence (rejected — out of scope per constitution).

---

### D-006: PDF Text Extraction — PyMuPDF (fitz)

**Decision**: Use `PyMuPDF` (imported as `fitz`) for PDF text extraction.
Call `fitz.open(stream=bytes, filetype="pdf")` to open from bytes without writing
to disk. Iterate pages with `page.get_text("text")` and concatenate results.
**Empty extraction**: If total extracted text (after stripping) is empty, raise a
structured `HTTPException(400, detail="No extractable text found in PDF...")`.
**Corrupt PDF**: Wrap `fitz.open` in try/except; `fitz.FileDataError` indicates
corruption — raise `HTTPException(400, detail="PDF is corrupted or unreadable.")`.
**Alternatives considered**: pdfminer.six (rejected — more complex API, slower for
simple extraction), pypdf (rejected — less reliable text extraction for some PDF types).

---

### D-007: File Validation Strategy

**Decision**: Validate in the following strict order before any processing:
1. **MIME type / extension check**: Accept only `text/plain` (.txt) and
   `application/pdf` (.pdf). Check both the file's `content_type` header and the
   filename extension.
2. **Size check**: Reject files > 10 MB (10 × 1024 × 1024 bytes).
3. **Content extraction** (PDF only): Attempt extraction; surface specific errors.
4. **Empty content check**: After extraction, reject if stripped text is empty.
**Rationale**: Validating before reading prevents resource exhaustion. The 10 MB limit
is a safe default for a dev-mode application. Checks are ordered cheapest-first.

---

### D-008: Statistics Calculation

**Decision**: All statistics are computed in the backend service, not the frontend.
Formulas:
- `char_count = len(original_text)`
- `word_count = len(original_text.split())`
- `token_count = len(tokens)`
- `tokens_per_word = token_count / word_count` (0.0 if word_count == 0)
- `tokens_per_char = token_count / char_count` (0.0 if char_count == 0)
Both floating-point values rounded to 4 decimal places in the response.

---

### D-009: API Communication Pattern

**Decision**: REST over HTTP. React uses the native `fetch` API (no extra HTTP client
library). All tokenization endpoints use `multipart/form-data` for file uploads
(FastAPI `UploadFile`). Text-only requests use `application/x-www-form-urlencoded`
or `multipart/form-data` with a text field. This avoids needing two different request
content types in the frontend.
**CORS**: FastAPI `CORSMiddleware` configured for `localhost` origins in development.
**Error contract**: All errors return `{"detail": "<human-readable string>"}` with
appropriate HTTP status codes (400 for client errors, 422 for validation, 500 for
unexpected server errors).
**Alternatives considered**: GraphQL (rejected — over-engineered for 2 endpoints),
axios (rejected — unnecessary dependency for simple fetch calls).

---

### D-010: UI Aesthetic — Neon-Gradient Cyberpunk Dark Mode

**Decision**: Dark background (`#0a0a0f`), neon accent palette:
- Primary neon: `#00f5ff` (cyan)
- Secondary neon: `#bf00ff` (violet)
- Accent neon: `#39ff14` (green)
- Warning neon: `#ff6b35` (orange)
- Gradient: `linear-gradient(135deg, #00f5ff, #bf00ff)`
Typography: `JetBrains Mono` for token display, `Inter` for UI text (Google Fonts).
Glassmorphism panels: `background: rgba(255,255,255,0.03)`, `backdrop-filter: blur(12px)`,
`border: 1px solid rgba(0,245,255,0.15)`.
Glow effects: `box-shadow: 0 0 20px rgba(0,245,255,0.3)` on interactive elements.
New vocabulary tokens: highlighted with neon green badge. Existing tokens: violet badge.
**Rationale**: Matches user's stated requirement for neon-gradient cyberpunk aesthetic.
Consistent use of CSS custom properties (variables) ensures the theme is maintainable
and easy to override.

---

### D-011: Testing Strategy

**Decision**:
- **Backend unit tests**: pytest. Test `TiktokenService`, `CustomTokenizerService`,
  `FileProcessor`, and `StatisticsCalculator` in isolation with mock/fixture data.
- **Backend integration tests**: pytest with `httpx.AsyncClient` + FastAPI `TestClient`.
  Test all API routes end-to-end with real service instances (no mocks for services).
- **Frontend tests**: React Testing Library + Vitest. Test component rendering, user
  interactions (tokenize button, file upload, tokenizer mode switch), loading/error
  states, and vocabulary panel updates.
**Alternatives considered**: Playwright for E2E (out of scope for this plan iteration),
Jest (replaced by Vitest for Vite-native integration).

---

### D-012: Security & Configuration

**Decision**: No authentication required (per spec). CORS restricted to localhost in
dev. File size limit enforced in the route handler before reading file bytes.
No secrets required — Tiktoken fetches its vocab files from OpenAI CDN on first use
and caches locally; this is Tiktoken's standard behaviour and requires no API keys.
Environment variable `MAX_UPLOAD_BYTES` (default: 10485760) controls the size limit,
making it configurable without code changes.
