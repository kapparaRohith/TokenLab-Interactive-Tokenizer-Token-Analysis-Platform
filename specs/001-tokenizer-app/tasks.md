# Tasks: Tokenizer Application

**Branch**: `001-tokenizer-app` | **Date**: 2026-09-27
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Data Model**: [data-model.md](./data-model.md) | **Contract**: [contracts/api-contract.md](./contracts/api-contract.md)

**Tech Stack**: Python 3.11+ · FastAPI · Pydantic · tiktoken · PyMuPDF · pytest · React 18 · TypeScript · Vite · Vitest · RTL

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize both project roots, install dependencies, and wire the build tooling. No functional code yet.

- [x] T001 Create repository root directory `tokenizer-app/` with `backend/` and `frontend/` subdirectories and top-level `README.md`
- [x] T002 Create `tokenizer-app/backend/requirements.txt` with pinned dependencies: `fastapi`, `uvicorn[standard]`, `tiktoken`, `PyMuPDF`, `pydantic`, `python-multipart`, `httpx`, `pytest`, `pytest-asyncio`
- [x] T003 [P] Create `tokenizer-app/backend/pytest.ini` configuring `testpaths = tests`, `asyncio_mode = auto`, and `python_files = test_*.py`
- [x] T004 [P] Create `tokenizer-app/backend/app/__init__.py`, `tokenizer-app/backend/app/services/__init__.py`, and `tokenizer-app/backend/app/routes/__init__.py` (empty init files for package structure)
- [x] T005 Scaffold `tokenizer-app/frontend/` using `npm create vite@latest . -- --template react-ts` (run inside `frontend/` directory); verify `package.json`, `vite.config.ts`, `tsconfig.json` are created
- [x] T006 [P] Install frontend dependencies: add `vitest`, `@vitest/ui`, `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom` to `tokenizer-app/frontend/package.json` devDependencies and run `npm install`
- [x] T007 [P] Configure Vitest in `tokenizer-app/frontend/vite.config.ts`: add `test` block with `globals: true`, `environment: 'jsdom'`, `setupFiles: './src/test-setup.ts'`; create `tokenizer-app/frontend/src/test-setup.ts` importing `@testing-library/jest-dom`
- [x] T008 [P] Add Google Fonts import for `Inter` and `JetBrains Mono` to `tokenizer-app/frontend/index.html` via `<link>` tags in `<head>`

**Checkpoint**: `pip install -r requirements.txt` succeeds; `npm run dev` starts Vite on port 5173; `pytest` runs with 0 tests collected (no errors); `npm run test` runs with 0 tests.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas, config, and shared infrastructure that ALL user stories depend on. Must be complete before any story implementation begins.

- [x] T009 Create `tokenizer-app/backend/app/config.py` defining `MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))` and `SUPPORTED_ENCODINGS: list[str] = ["cl100k_base", "p50k_base", "p50k_edit", "r50k_base", "o200k_base"]`
- [x] T010 [P] Create `tokenizer-app/backend/app/schemas.py` with all Pydantic models exactly as specified in `contracts/api-contract.md`: `TokenizerMode` (enum: tiktoken/custom), `SourceType` (enum: text/txt/pdf), `TokenSchema` (index: int, token_id: int, token_text: str), `VocabularyEntrySchema` (token_id: int, token_text: str, frequency: int, is_new: bool), `TokenizationResultSchema` (all 14 fields from contract), `EncodingsResponseSchema`, `ResetResponseSchema`, `HealthResponseSchema`
- [x] T011 Create `tokenizer-app/backend/app/main.py` with: FastAPI app instance, `CORSMiddleware` configured for `allow_origins=["http://localhost:5173"]` with `allow_methods=["*"]` and `allow_headers=["*"]`, router include for `tokenize.py`, and `GET /health` route returning `{"status": "ok"}`
- [x] T012 [P] Create `tokenizer-app/frontend/src/types/api.ts` with all TypeScript interfaces exactly as specified in `contracts/api-contract.md`: `TokenizerMode`, `SourceType`, `Token`, `VocabularyEntry`, `TokenizationResult` (14 fields), `EncodingsResponse`, `ResetResponse`, `ApiError`
- [x] T013 [P] Create `tokenizer-app/frontend/src/styles/index.css` with the complete neon-gradient cyberpunk dark-mode theme: CSS custom properties (`--bg-primary: #0a0a0f`, `--neon-cyan: #00f5ff`, `--neon-violet: #bf00ff`, `--neon-green: #39ff14`, `--neon-orange: #ff6b35`, `--gradient-primary: linear-gradient(135deg, #00f5ff, #bf00ff)`, `--border-glow`, `--shadow-glow`, `--font-mono`, `--font-ui`); global reset; glassmorphism panel class (`.glass-panel`); neon button styles (`.btn-primary`, `.btn-secondary`, `.btn-danger`); badge styles (`.badge-new`, `.badge-existing`); loading spinner animation (`@keyframes neon-pulse`)
- [x] T014 Create `tokenizer-app/backend/tests/conftest.py` with shared pytest fixtures: `client` (FastAPI `TestClient`), `sample_txt_bytes` (b"Hello world sample text"), `sample_pdf_bytes` (a minimal valid PDF bytes fixture using PyMuPDF or a hardcoded minimal PDF bytestring)

**Checkpoint**: `python -c "from app.schemas import TokenizationResultSchema; print('OK')"` succeeds; `python -c "from app.main import app; print('OK')"` succeeds; `npm run build` compiles TypeScript without errors.

---

## Phase 3: User Story 1 — Direct Text Tokenization (Priority: P1) ⭐ MVP

**Goal**: Users can enter text, select Tiktoken mode with an encoding, click Tokenize, and see a token table and statistics panel. This is the core MVP.

**Independent Test**: Enter "Hello world!" with Tiktoken / cl100k_base → token table shows 3 rows with correct IDs and stats show char_count=12, word_count=2.

### Backend — Statistics Service

- [x] T015 [P] [US1] Create `tokenizer-app/backend/app/services/statistics.py` with four pure functions: `char_count(text: str) -> int` (returns `len(text)`), `word_count(text: str) -> int` (returns `len(text.split())`), `tokens_per_word(token_count: int, word_count: int) -> float` (safe divide, rounded to 4 decimal places, returns 0.0 if word_count==0), `tokens_per_char(token_count: int, char_count: int) -> float` (safe divide, rounded to 4 decimal places, returns 0.0 if char_count==0)
- [x] T016 [P] [US1] Create `tokenizer-app/backend/tests/test_statistics.py` testing all four functions: normal inputs, zero word_count edge case, zero char_count edge case, empty string, single character, single word

### Backend — TiktokenService

- [x] T017 [US1] Create `tokenizer-app/backend/app/services/tiktoken_service.py` with class `TiktokenService`: module-level `_encoding_cache: dict[str, tiktoken.Encoding] = {}` for caching; `SUPPORTED_ENCODINGS` imported from `config.py`; method `get_encoding(name: str) -> tiktoken.Encoding` that checks cache or calls `tiktoken.get_encoding(name)` and caches; method `tokenize(text: str, encoding: str) -> list[TokenSchema]` that validates encoding against `SUPPORTED_ENCODINGS` (raises `ValueError` with message `"Unsupported encoding: '{encoding}'. Supported: {', '.join(SUPPORTED_ENCODINGS)}"` if invalid), calls `enc.encode(text)` for token IDs, decodes each via `enc.decode_single_token_bytes(id)` with UTF-8 decode and `<0xXX>` hex fallback for non-UTF-8 bytes, returns list of `TokenSchema(index=i, token_id=id, token_text=text)`; MUST NOT modify any Tiktoken output
- [x] T018 [US1] Create `tokenizer-app/backend/tests/test_tiktoken_service.py` testing: tokenize "Hello world!" with cl100k_base returns correct token count and IDs matching `tiktoken.get_encoding("cl100k_base").encode("Hello world!")` directly (SC-006); invalid encoding raises ValueError; each supported encoding in `SUPPORTED_ENCODINGS` can be loaded without error; non-UTF-8 bytes produce hex-escaped token_text (not a crash)

### Backend — Text Route

- [x] T019 [US1] Create `tokenizer-app/backend/app/routes/tokenize.py` with router `APIRouter(prefix="/tokenize")`; implement `GET /encodings` returning `EncodingsResponseSchema(encodings=SUPPORTED_ENCODINGS)`; implement `POST /text` accepting `Form` fields `text: str`, `tokenizer: str`, `encoding: str | None = None`: validate `text.strip()` is non-empty (raise `HTTPException(400, "Input text cannot be empty.")`); dispatch to `TiktokenService.tokenize()` or `CustomTokenizerService.tokenize()` based on tokenizer field; catch `ValueError` from services and re-raise as `HTTPException(400, detail=str(e))`; compute statistics via `statistics.py` functions; assemble and return `TokenizationResultSchema`; route handler MUST contain no business logic beyond dispatch and assembly
- [x] T020 [US1] Add route tests in `tokenizer-app/backend/tests/test_routes.py`: `GET /health` returns 200 `{"status":"ok"}`; `GET /tokenize/encodings` returns 200 with all 5 encodings; `POST /tokenize/text` with valid text+tiktoken+cl100k_base returns 200 with all 14 required fields populated (SC-002); `POST /tokenize/text` with whitespace-only text returns 400; `POST /tokenize/text` with unsupported encoding returns 400

### Frontend — API Service & Core State

- [x] T021 [US1] Create `tokenizer-app/frontend/src/services/api.ts` with four functions: `fetchEncodings(): Promise<string[]>` (GET /tokenize/encodings, extracts `.encodings`); `tokenizeText(text: string, tokenizer: TokenizerMode, encoding?: string): Promise<TokenizationResult>` (POST /tokenize/text as multipart FormData); `tokenizeFile(file: File, tokenizer: TokenizerMode, encoding?: string): Promise<TokenizationResult>` (POST /tokenize/file as multipart FormData); `resetVocabulary(): Promise<void>` (POST /tokenize/custom/reset); all functions parse `{"detail": "..."}` from non-2xx responses and throw as `ApiError`; use native `fetch` only, no axios
- [x] T022 [US1] Create `tokenizer-app/frontend/src/components/ErrorMessage.tsx`: renders a dismissible neon-orange alert div when `error` prop (string | null) is non-null; includes an × button calling `onDismiss` prop; applies `--neon-orange` border-glow style from CSS custom properties; renders null when error is null
- [x] T023 [US1] Create `tokenizer-app/frontend/src/components/TokenizerControls.tsx`: renders a segmented toggle for `tokenizerMode` ('tiktoken'/'custom') using neon-gradient active state; when mode is 'tiktoken' renders a `<select>` populated from `availableEncodings` prop with `selectedEncoding` value and `onEncodingChange` handler; when mode is 'custom' the encoding selector is hidden (not just visually hidden — conditional render); all interactive elements have `aria-label` attributes
- [x] T024 [US1] Create `tokenizer-app/frontend/src/components/StatisticsPanel.tsx`: receives `result: TokenizationResult | null`; when null renders an empty state placeholder with neon border; when populated renders 5 glassmorphism stat cards (`.glass-panel`) for: Character Count, Word Count, Token Count, Tokens/Word, Tokens/Char; each card has a neon-cyan numeric value and a label; uses `--font-mono` for numbers
- [x] T025 [US1] Create `tokenizer-app/frontend/src/components/TokenTable.tsx`: receives `tokens: Token[]`; renders a scrollable table (max-height with overflow-y: auto) with columns: Index, Token ID, Token Text; monospace font (`--font-mono`) for all cells; alternating row background tints in near-black; empty state message when tokens array is empty; each row uses `token.index` as React key
- [x] T026 [US1] Create `tokenizer-app/frontend/src/components/TokenizeButton.tsx`: receives `isLoading: boolean`, `onClick: () => void`, `disabled: boolean`; renders a gradient button (`.btn-primary`) with label "Tokenize"; when `isLoading` shows a neon-cyan pulsing spinner (CSS `neon-pulse` animation) and disables the button; when `disabled` (e.g. empty input) also disables button
- [x] T027 [US1] Create `tokenizer-app/frontend/src/components/InputPanel.tsx`: renders three mode tabs ("Text", "TXT", "PDF") as neon-bordered tab buttons; in Text mode renders a `<textarea>` with `--neon-cyan` focus glow border; emits `onTextChange(text: string)` as user types; client-side empty check: if textarea is empty/whitespace on submit trigger, call `onValidationError("Input cannot be empty.")` without making API call (FR-031)
- [x] T028 [US1] Create `tokenizer-app/frontend/src/App.tsx`: manage all state as defined in plan.md (`inputMode`, `textInput`, `uploadedFile`, `tokenizerMode`, `selectedEncoding`, `availableEncodings`, `result`, `isLoading`, `error`); `useEffect` on mount to call `fetchEncodings()` and populate `availableEncodings` and set default `selectedEncoding` to first encoding; `handleTokenize()` dispatches `tokenizeText` or `tokenizeFile` based on mode, sets `isLoading` true before call and false after, sets `result` on success or `error` on failure; render: app title (h1 with gradient text), description paragraph, `InputPanel`, `TokenizerControls`, `TokenizeButton`, `ErrorMessage`, `StatisticsPanel`, `TokenTable`; vocabulary panel and extracted text panel rendered conditionally (null in US1 — wired in later stories); import `./styles/index.css`

### Frontend — Tests (US1)

- [x] T029 [P] [US1] Create `tokenizer-app/frontend/tests/StatisticsPanel.test.tsx`: test renders 5 stat cards with correct values when result is provided; test renders empty state when result is null
- [x] T030 [P] [US1] Create `tokenizer-app/frontend/tests/TokenTable.test.tsx`: test renders correct number of rows matching tokens array length; test renders all column headers (Index, Token ID, Token Text); test renders empty state when tokens is empty array
- [x] T031 [P] [US1] Create `tokenizer-app/frontend/tests/App.test.tsx`: mock `fetchEncodings` to return `["cl100k_base"]`; test encodings are fetched on mount and encoding select is populated; mock `tokenizeText` to return a fixture result; test clicking Tokenize calls tokenizeText with correct args; test loading state disables Tokenize button; test error from API displays in ErrorMessage

**Checkpoint**: `pytest tests/test_tiktoken_service.py tests/test_statistics.py tests/test_routes.py -k "not file"` all pass; `npm run test` StatisticsPanel, TokenTable, App tests pass; curl V-001, V-002, V-003 from quickstart.md return expected responses; open browser, type text, click Tokenize → token table and stats appear.

---

## Phase 4: User Story 7 — Input Validation & Error Handling (Priority: P1)

**Goal**: All invalid inputs produce specific, human-readable error messages. UI recovers gracefully. This is P1 because it is required for production-quality of the core MVP.

**Independent Test**: Submit empty text → client-side error shown, no API call made; submit unsupported encoding → 400 with specific message; submit whitespace-only text → 400.

### Backend — Validation Completeness

- [x] T032 [US7] Add remaining validation test cases to `tokenizer-app/backend/tests/test_routes.py`: `POST /tokenize/text` with missing `tokenizer` field returns 422; `POST /tokenize/text` with `tokenizer=tiktoken` and no `encoding` field returns 400 with message about encoding being required; `POST /tokenize/text` with unsupported encoding `gpt2` returns 400 with detail containing `gpt2`; verify all error responses have shape `{"detail": "..."}` (string, not object)
- [x] T033 [US7] Update `tokenizer-app/backend/app/routes/tokenize.py` `POST /text` handler to explicitly validate that `encoding` is provided and non-empty when `tokenizer == "tiktoken"` (raise `HTTPException(400, "Encoding is required for Tiktoken mode.")` if missing); add global `exception_handler` in `main.py` for unhandled `Exception` that returns `HTTPException(500, "An unexpected server error occurred.")` without exposing stack trace

### Frontend — Validation Completeness

- [x] T034 [US7] Update `tokenizer-app/frontend/src/components/InputPanel.tsx` to enforce client-side validation before any API call: empty/whitespace text → call `onValidationError("Input cannot be empty.")` (FR-031); no file selected when in TXT or PDF mode → call `onValidationError("Please select a file to upload.")`; wrong file extension for selected mode → call `onValidationError("Please select a .txt file.")` or `"...a .pdf file."`; none of these trigger an API request
- [x] T035 [P] [US7] Update `tokenizer-app/frontend/tests/App.test.tsx` and `tokenizer-app/frontend/tests/InputPanel.test.tsx`: test empty textarea submit shows error and does NOT call tokenizeText; test API error response displays detail in ErrorMessage; test error dismisses on × click; test error clears when new tokenization starts

**Checkpoint**: All 5 validation scenarios from SC-004 produce specific messages; `pytest tests/test_routes.py` all pass; curl V-009, V-011 from quickstart.md return expected 400 responses.

---

## Phase 5: User Story 2 — TXT File Upload (Priority: P2)

**Goal**: Users can upload a .txt file; extracted text is displayed; tokenization proceeds using the extracted text.

**Independent Test**: Upload a `.txt` file → extracted text section appears with file content; tokenization succeeds → token table populated.

### Backend — FileProcessor (TXT)

- [x] T036 [US2] Create `tokenizer-app/backend/app/services/file_processor.py` with class `FileProcessor` and static method `extract_text(file_bytes: bytes, filename: str, content_type: str) -> tuple[str, SourceType]`: check file extension (`.lower().endswith`) and content_type against allowed types `.txt` / `.pdf` (raise `HTTPException(400, "Unsupported file type. Only .txt and .pdf files are accepted.")` if neither); check `len(file_bytes) > MAX_UPLOAD_BYTES` (raise `HTTPException(413, "File too large. Maximum allowed size is 10 MB.")`); for TXT: decode `file_bytes.decode("utf-8", errors="replace")`, strip, check empty (raise `HTTPException(400, "The uploaded file contains no text content.")`), return `(text, SourceType.txt)`; PDF path stubbed for US3
- [x] T037 [US2] Create `tokenizer-app/backend/tests/test_file_processor.py` testing TXT path: valid UTF-8 txt bytes returns extracted string and SourceType.txt; whitespace-only txt returns 400; unsupported file type (.docx) returns 400 with message about .txt and .pdf; file exceeding 10 MB returns 413; latin-1 characters decoded with errors="replace" does not raise
- [x] T038 [US2] Add `POST /file` route to `tokenizer-app/backend/app/routes/tokenize.py` accepting `UploadFile` (field name `file`), `tokenizer: str = Form(...)`, `encoding: str | None = Form(None)`; call `FileProcessor.extract_text(await file.read(), file.filename, file.content_type)`; dispatch to selected tokenizer service with extracted text; compute statistics; assemble `TokenizationResultSchema` with correct `source_type`; route handler MUST remain a thin controller
- [x] T039 [US2] Add TXT route tests to `tokenizer-app/backend/tests/test_routes.py`: `POST /tokenize/file` with valid txt returns 200, `source_type="txt"`, `original_text` matches file content; `POST /tokenize/file` with .docx returns 400; `POST /tokenize/file` with oversized file returns 413; `POST /tokenize/file` with empty txt returns 400

### Frontend — TXT Upload UI

- [x] T040 [US2] Update `tokenizer-app/frontend/src/components/InputPanel.tsx` TXT tab: render a file `<input accept=".txt">` with neon styled drag-area or button; on file selection store File object and display filename; emit `onFileChange(file: File)` to App; client-side: validate file extension is `.txt` before calling `onValidationError`
- [x] T041 [US2] Create `tokenizer-app/frontend/src/components/ExtractedTextPanel.tsx`: receives `text: string | null` and `sourceType: SourceType | null`; renders null when text is null; when populated renders a collapsible glassmorphism panel with heading "Extracted Text" and the extracted text in a scrollable `<pre>` with `--font-mono`; collapse toggle button with neon arrow icon
- [x] T042 [US2] Update `tokenizer-app/frontend/src/App.tsx` to wire TXT file mode: when inputMode is 'txt' pass `onFileChange` to `InputPanel`; update `handleTokenize()` to call `tokenizeFile(uploadedFile, tokenizerMode, selectedEncoding)` when inputMode is 'txt'; after successful result set `result` and render `ExtractedTextPanel` with `result.original_text` when `result.source_type` is 'txt' or 'pdf'
- [x] T043 [P] [US2] Create `tokenizer-app/frontend/tests/InputPanel.test.tsx`: test TXT tab renders file input; test file selection stores file; test wrong extension shows validation error without API call

**Checkpoint**: Upload a valid `.txt` file → extracted text panel shows content → tokenize → token table populated; curl V-007 and V-010 from quickstart.md pass; `pytest tests/test_file_processor.py tests/test_routes.py` all pass.

---

## Phase 6: User Story 3 — PDF File Upload (Priority: P2)

**Goal**: Users can upload a text-based PDF; backend extracts text; extracted text displayed; tokenization proceeds.

**Independent Test**: Upload a text-based PDF → extracted text section shows PDF content; upload corrupted PDF → specific error message; upload image-only PDF → distinct "no extractable text" error.

### Backend — FileProcessor (PDF)

- [x] T044 [US3] Complete PDF extraction in `tokenizer-app/backend/app/services/file_processor.py`: in the `.pdf` branch call `fitz.open(stream=file_bytes, filetype="pdf")` inside `try/except fitz.FileDataError as e` (raise `HTTPException(400, "PDF is corrupted or unreadable.")`); iterate `doc` pages calling `page.get_text("text")`; concatenate all page text; strip result; if empty raise `HTTPException(400, "No extractable text found in PDF. The file may contain only images or scanned content.")` (distinct message from corrupted); return `(text, SourceType.pdf)`
- [x] T045 [US3] Add PDF tests to `tokenizer-app/backend/tests/test_file_processor.py`: valid text-based PDF bytes return extracted text and SourceType.pdf; corrupted PDF bytes raise 400 "corrupted or unreadable"; valid PDF with no text raises 400 "No extractable text"; create test fixtures using `fitz.open()` to generate minimal in-memory test PDFs (a PDF with one text page, a PDF with no text pages)
- [x] T046 [US3] Add PDF route tests to `tokenizer-app/backend/tests/test_routes.py`: `POST /tokenize/file` with valid text PDF returns 200 `source_type="pdf"`; corrupted PDF bytes returns 400 with corruption message; image-only PDF returns 400 with extractable text message (V-008 scenario)

### Frontend — PDF Upload UI

- [x] T047 [US3] Update `tokenizer-app/frontend/src/components/InputPanel.tsx` PDF tab: render a file `<input accept=".pdf">` with same neon styled drag-area; emit `onFileChange(file: File)` to App; client-side: validate extension is `.pdf`
- [x] T048 [US3] Update `tokenizer-app/frontend/src/App.tsx` PDF mode: when inputMode is 'pdf' wire file input to `handleTokenize()` calling `tokenizeFile` with the PDF file; `ExtractedTextPanel` already conditionally rendered from US2 — no additional wiring needed beyond inputMode 'pdf' routing

**Checkpoint**: Upload text-based PDF → extracted text appears → tokenize works; upload corrupt PDF → "corrupted or unreadable" error shown; curl V-008 from quickstart.md passes; all `test_file_processor.py` tests pass.

---

## Phase 7: User Story 4 — Tiktoken Encoding Selection (Priority: P2)

**Goal**: Users can switch between all supported Tiktoken encodings and see different tokenization results for the same input.

**Independent Test**: Tokenize "Hello world!" with cl100k_base then p50k_base → token counts differ; encoding name shown in result matches selected encoding.

### Backend — Encoding Listing

- [x] T049 [US4] Verify `GET /tokenize/encodings` route (created in T019) returns all 5 encodings from `SUPPORTED_ENCODINGS` in `config.py`; add test in `test_routes.py` asserting all 5 names present in response; confirm `POST /tokenize/text` with each of the 5 encodings returns 200 (one test per encoding using parametrize)

### Frontend — Encoding Selector

- [x] T050 [US4] Verify `TokenizerControls.tsx` (created in T023) encoding `<select>` is populated from `availableEncodings` fetched on mount; add test in `tokenizer-app/frontend/tests/App.test.tsx` asserting that after mount with mocked `fetchEncodings` returning 5 encodings, the encoding select has 5 options; test switching encoding re-selects value correctly

**Checkpoint**: Open app → Tiktoken mode → encoding select shows all 5 options; select p50k_base, tokenize same text → token IDs differ from cl100k_base; curl V-002 and V-004 from quickstart.md pass.

---

## Phase 8: User Story 5 — Token Results Visualization (Priority: P2)

**Goal**: Token table and statistics panel render accurately for all successful tokenization responses.

**Independent Test**: After any successful tokenization the table row count equals `result.token_count` and all 5 stats are mathematically consistent.

### Backend — Full Schema Validation

- [x] T051 [US5] Add parametrized test in `tokenizer-app/backend/tests/test_routes.py` asserting SC-002 for all input paths: for `POST /tokenize/text` with tiktoken and custom mode, verify response contains all 14 required fields: `original_text`, `source_type`, `tokenizer`, `encoding`, `token_count`, `tokens`, `token_ids`, `token_texts`, `char_count`, `word_count`, `tokens_per_word`, `tokens_per_char`, `vocabulary` (null for tiktoken), `new_token_ids` (null for tiktoken); assert `len(result["tokens"]) == result["token_count"]`; assert `len(result["token_ids"]) == result["token_count"]`

### Frontend — Visualization Polish

- [x] T052 [P] [US5] Update `tokenizer-app/frontend/src/components/TokenTable.tsx` to display full token detail: ensure each row shows index (0-based), token_id, and token_text; apply `--font-mono` to token_text column; add hover row highlight using neon-cyan at 10% opacity; add a row-count badge above the table showing "N tokens"
- [x] T053 [P] [US5] Update `tokenizer-app/frontend/src/components/StatisticsPanel.tsx` to display all 5 metrics with correct formatting: token_count as integer; tokens_per_word and tokens_per_char to 4 decimal places; add neon-gradient top border accent to each card
- [x] T054 [P] [US5] Update `tokenizer-app/frontend/tests/TokenTable.test.tsx` and `tokenizer-app/frontend/tests/StatisticsPanel.test.tsx` with additional assertions: row count matches tokens array length; all 5 stat cards render correct values from fixture result; tokens_per_word rendered with 4 decimal places

**Checkpoint**: Tokenize any text → row count badge shows correct number; stats panel shows all 5 values; manually verify tokens_per_word = token_count / word_count (4dp) for a known input.

---

## Phase 9: User Story 6 — Custom Vocabulary Management (Priority: P3)

**Goal**: Custom Tokenizer builds and displays its in-memory vocabulary; new tokens highlighted in neon green; existing tokens shown in violet; vocabulary resets on demand.

**Independent Test**: Tokenize "hello world" with custom → vocabulary panel shows 2 new entries (green); tokenize again → 0 new entries, frequencies=2 (violet); click Reset → vocabulary clears; tokenize again → all new again.

### Backend — CustomTokenizerService

- [x] T055 [US6] Create `tokenizer-app/backend/app/services/custom_tokenizer_service.py` with class `CustomTokenizerService`: compile regex pattern at module level `PATTERN = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d|\s*[a-zA-Z]+|\d+|[^\s\w]")`; instance state: `_vocab: dict[str, VocabularyEntrySchema] = {}` and `_next_id: int = 0`; method `tokenize(text: str) -> tuple[list[TokenSchema], list[VocabularyEntrySchema], list[int]]`: call `re.findall(PATTERN, text)` to get raw token strings; for each token string look up `_vocab` by token_text — if found increment frequency and mark `is_new=False`; if not found create entry with `token_id=_next_id`, `frequency=1`, `is_new=True`, increment `_next_id`; build `TokenSchema` list with 0-based index, stable token_id, and token_text; return (tokens, sorted vocabulary snapshot, new_token_ids); method `reset() -> None`: sets `_vocab = {}` and `_next_id = 0`; method `get_vocabulary() -> list[VocabularyEntrySchema]`: returns list sorted by token_id
- [x] T056 [US6] Add `POST /tokenize/custom/reset` route to `tokenizer-app/backend/app/routes/tokenize.py`: call `custom_service.reset()`, return `ResetResponseSchema(message="Custom tokenizer vocabulary has been reset.")`; inject `CustomTokenizerService` as a module-level singleton (instantiated once in routes file or via FastAPI `Depends` with a module-level instance)
- [x] T057 [US6] Create `tokenizer-app/backend/tests/test_custom_tokenizer_service.py` testing: regex split of "Hello world!" produces expected token list; same input tokenized twice produces identical token IDs (SC-003 determinism); first call marks all tokens `is_new=True`; second call marks all tokens `is_new=False` and doubles frequencies; `reset()` clears vocabulary and resets next_id to 0; after reset, next tokenization re-creates entries with `is_new=True` starting from id 0; mixed new+existing tokens in a single call correctly flag only new ones; token_id values are unique and dense starting at 0
- [x] T058 [US6] Add custom tokenizer route tests to `tokenizer-app/backend/tests/test_routes.py`: `POST /tokenize/text` with custom mode returns 200 with non-null `vocabulary` and `new_token_ids`; second call same text returns empty `new_token_ids` and doubled frequencies; `POST /tokenize/custom/reset` returns 200 with reset message; after reset, next custom tokenization again returns all `is_new=True`

### Frontend — VocabularyPanel

- [x] T059 [US6] Create `tokenizer-app/frontend/src/components/VocabularyPanel.tsx`: receives `vocabulary: VocabularyEntry[] | null`, `newTokenIds: number[] | null`, `onReset: () => void`; renders null when vocabulary is null or tokenizerMode is not 'custom'; renders a glassmorphism panel with heading "Custom Vocabulary" and entry count badge; renders a table with columns: ID, Token, Frequency, Status; Status column shows `.badge-new` (neon green, label "NEW") when `entry.is_new` is true and `.badge-existing` (neon violet, label "EXISTING") otherwise; renders a "Reset Vocabulary" button (`.btn-danger`) that calls `onReset` prop; empty state message when vocabulary is empty array
- [x] T060 [US6] Update `tokenizer-app/frontend/src/App.tsx` to wire vocabulary: add `handleReset()` calling `resetVocabulary()` API then clearing `result` and `error`; pass `result.vocabulary`, `result.new_token_ids`, and `handleReset` to `VocabularyPanel`; render `VocabularyPanel` conditionally when `tokenizerMode === 'custom'`
- [x] T061 [P] [US6] Create `tokenizer-app/frontend/tests/VocabularyPanel.test.tsx`: test renders null when vocabulary is null; test renders one row per vocabulary entry; test NEW badge shown when `is_new=true`; test EXISTING badge shown when `is_new=false`; test reset button click calls `onReset` handler; test entry count badge shows correct count; test empty vocabulary shows empty state message

**Checkpoint**: Run curl V-004, V-005, V-006 from quickstart.md; all pass. In browser: tokenize custom → green NEW badges; tokenize again → violet EXISTING badges; click Reset → vocabulary clears; `pytest tests/test_custom_tokenizer_service.py tests/test_routes.py` all pass; `npm run test VocabularyPanel` passes.

---

## Phase 10: User Story 8 — Responsive & Accessible Interface (Priority: P3)

**Goal**: Application is fully usable at ≥768px without horizontal scroll; all controls keyboard-navigable; all interactive elements labelled.

**Independent Test**: Resize to 768px width — no horizontal scroll; Tab through all controls — all reachable; loading state disables Tokenize button.

- [x] T062 [US8] Add responsive layout rules to `tokenizer-app/frontend/src/styles/index.css`: single-column stack layout at ≥768px using CSS Grid or Flexbox with `flex-wrap: wrap`; ensure token table uses `overflow-x: auto` on its container to prevent horizontal overflow; ensure vocabulary table uses `overflow-x: auto`; add `@media (max-width: 1024px)` breakpoint rules for side-by-side panels stacking to vertical
- [x] T063 [US8] Audit all interactive elements in all components for accessibility: add `aria-label` to all icon buttons (Reset, close/×, collapse toggle); add `role="status"` and `aria-live="polite"` to `ErrorMessage.tsx`; add `aria-label="Token table"` to `TokenTable.tsx` `<table>`; add `aria-label="Vocabulary table"` to `VocabularyPanel.tsx` `<table>`; add `aria-busy` attribute to `TokenizeButton.tsx` when loading; verify all `<input>` and `<select>` elements have associated `<label>` elements
- [x] T064 [US8] Update `tokenizer-app/frontend/tests/App.test.tsx`: test that Tokenize button has `aria-busy="true"` during loading; test ErrorMessage has `role="status"`; test all form controls have accessible labels (use `getByLabelText` queries)

**Checkpoint**: Manual tab navigation cycles through all controls in logical order; loading spinner renders with aria-busy; no horizontal scroll at 768px viewport; `npm run test` all accessibility tests pass.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, visual polish, documentation, and validation sign-off.

- [x] T065 Add `tokenizer-app/backend/app/main.py` startup event to pre-load all Tiktoken encodings on app start (calls `TiktokenService.get_encoding(enc)` for each in `SUPPORTED_ENCODINGS`) so first tokenization request is not slow due to BPE model download; log startup message
- [x] T066 [P] Add `tokenizer-app/frontend/src/styles/index.css` micro-animation polish: neon-glow pulse on token table rows on mount (CSS `@keyframes row-appear` with opacity 0→1 and subtle translateY); hover glow intensification on stat cards; active press effect on `.btn-primary`
- [x] T067 [P] Update `tokenizer-app/frontend/src/App.tsx` to clear stale `result` when `tokenizerMode` changes (switching from Tiktoken to Custom or vice versa resets the results area to empty state — avoids showing tiktoken vocabulary panel data with custom tokenizer UI)
- [x] T068 [P] Update `tokenizer-app/frontend/src/App.tsx` to clear `result` and `error` when `inputMode` changes (switching from Text to TXT or PDF tabs resets the form state)
- [x] T069 Add `tokenizer-app/README.md` with: project overview, prerequisites, backend setup commands (`pip install -r requirements.txt && uvicorn app.main:app --reload`), frontend setup commands (`npm install && npm run dev`), link to quickstart.md for validation scenarios
- [x] T070 Run full pytest suite from `tokenizer-app/backend/`: all tests must pass with 0 failures and 0 errors; record passing test count
- [x] T071 Run full Vitest suite from `tokenizer-app/frontend/`: all tests must pass with 0 failures; record passing test count
- [x] T072 Execute all 12 quickstart validation scenarios (V-001 through V-012) from `quickstart.md`; record pass/fail for each; all must pass before marking implementation complete

**Checkpoint**: All 72 tasks complete; `pytest` green; `npm run test` green; all quickstart scenarios pass; manual browser walkthrough (US Story 8, V-012) confirms full end-to-end flow.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user story phases
- **Phase 3 (US1 — Text Tokenization)**: Depends on Phase 2 — **Critical path; start first**
- **Phase 4 (US7 — Validation)**: Depends on Phase 3 (routes exist to test against)
- **Phase 5 (US2 — TXT Upload)**: Depends on Phase 2; can start in parallel with Phase 3
- **Phase 6 (US3 — PDF Upload)**: Depends on Phase 5 (FileProcessor TXT path must exist)
- **Phase 7 (US4 — Encoding Selection)**: Depends on Phase 3 (Tiktoken route must exist)
- **Phase 8 (US5 — Visualization)**: Depends on Phase 3 (results shape must exist)
- **Phase 9 (US6 — Custom Vocabulary)**: Depends on Phase 2 (schemas) and Phase 3 (route structure)
- **Phase 10 (US8 — Accessibility)**: Depends on all component phases (3, 5, 6, 9)
- **Phase 11 (Polish)**: Depends on all user story phases complete

### Parallel Opportunities by Phase

```
Phase 1: T001 → T002 → [T003 ∥ T004 ∥ T005] → [T006 ∥ T007 ∥ T008]

Phase 2: T009 → [T010 ∥ T011 ∥ T012 ∥ T013] → T014

Phase 3: [T015 ∥ T016] → T017 → T018 → T019 → T020
         [T021 ∥ T022 ∥ T023 ∥ T024 ∥ T025 ∥ T026 ∥ T027] → T028
         [T029 ∥ T030 ∥ T031] (can run once components exist)

Phase 5: T036 → T037 → T038 → T039  (backend)
         T040 → T041 → T042  (frontend, parallel with backend)
         T043 (parallel with T040-T042)

Phase 9: T055 → T056 → T057 → T058  (backend)
         T059 → T060  (frontend, parallel with backend)
         T061 (parallel with T059-T060)
```

### User Story Dependency Graph

```
Phase 2 (Foundation)
  ├──► Phase 3 (US1 - P1) ──► Phase 4 (US7 - P1) ──► Phase 10 (US8 - P3)
  ├──► Phase 5 (US2 - P2) ──► Phase 6 (US3 - P2) ──► Phase 10
  ├──► Phase 7 (US4 - P2) ──► Phase 8 (US5 - P2) ──► Phase 10
  └──► Phase 9 (US6 - P3) ──────────────────────────► Phase 10
                                                            │
                                                      Phase 11 (Polish)
```

---

## Implementation Strategy

### MVP First (Phase 1 + 2 + 3 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (schemas, config, theme, main.py)
3. Complete Phase 3: US1 — Direct Text Tokenization
4. **STOP and VALIDATE**: curl V-001, V-002, V-003; open browser, type text, tokenize
5. All P1 requirements satisfied; demo-ready

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 (Phase 3) → text tokenization MVP ✅
3. US7 (Phase 4) → hardened validation ✅
4. US2 (Phase 5) → TXT upload ✅
5. US3 (Phase 6) → PDF upload ✅
6. US4 (Phase 7) → encoding selection ✅
7. US5 (Phase 8) → visualization polish ✅
8. US6 (Phase 9) → custom vocabulary ✅
9. US8 (Phase 10) → accessibility ✅
10. Polish (Phase 11) → full quickstart validation ✅

---

## Notes

- `[P]` tasks operate on different files with no shared in-progress dependencies — safe to parallelize
- `[US#]` labels map directly to user stories in `spec.md` for full traceability
- Backend and frontend Phases 3–9 can be developed in parallel by two developers after Phase 2 is complete
- Test tasks are included per spec requirement that "backend tests MUST use pytest; frontend behavior MUST have appropriate automated tests" (constitution Principle VII)
- Commit after each checkpoint to enable clean rollback
- Do not start Phase 3+ until Phase 2 checkpoint passes — schemas and config are load-bearing for all subsequent tasks
