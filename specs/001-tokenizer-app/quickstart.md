# Quickstart Validation Guide: Tokenizer Application

**Feature**: 001-tokenizer-app
**Date**: 2026-09-27
**Purpose**: Prove the feature works end-to-end via runnable validation scenarios.

See [API Contract](./contracts/api-contract.md) for full schema details.
See [Data Model](./data-model.md) for entity definitions.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | python.org |
| Node.js | 18+ | nodejs.org |
| pip | latest | bundled with Python |
| npm | 9+ | bundled with Node.js |

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend is ready when you see: `Uvicorn running on http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend is ready when Vite reports: `Local: http://localhost:5173`

---

## Validation Scenarios

### V-001: Health Check

**Validates**: Backend is running and reachable.

```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{ "status": "ok" }
```

---

### V-002: Supported Encodings

**Validates**: FR-011 — Encoding list is available.

```bash
curl http://localhost:8000/tokenize/encodings
```

**Expected**: JSON with `encodings` array containing at minimum:
`cl100k_base`, `p50k_base`, `p50k_edit`, `r50k_base`, `o200k_base`.

---

### V-003: Tiktoken Text Tokenization

**Validates**: FR-015, FR-016, FR-017, SC-001, SC-002, SC-006.

```bash
curl -X POST http://localhost:8000/tokenize/text \
  -F "text=Hello world!" \
  -F "tokenizer=tiktoken" \
  -F "encoding=cl100k_base"
```

**Expected**:
- HTTP 200
- `token_count` equals length of `tokens` array
- `tokens[0].token_text` equals `"Hello"` (or leading-space variant)
- `char_count` = 12, `word_count` = 2
- `vocabulary` is null, `new_token_ids` is null
- Token IDs match what `tiktoken.get_encoding("cl100k_base").encode("Hello world!")` produces

---

### V-004: Custom Tokenizer — First Call (New Tokens)

**Validates**: FR-018, FR-019, FR-020, FR-021, FR-022, FR-023.

```bash
curl -X POST http://localhost:8000/tokenize/text \
  -F "text=Hello world!" \
  -F "tokenizer=custom"
```

**Expected**:
- HTTP 200
- All tokens in `new_token_ids` (all are new on first call)
- `vocabulary` contains entries with `is_new: true`
- Each `VocabularyEntry.token_id` is unique and starts at 0

---

### V-005: Custom Tokenizer — Second Call (Existing Tokens)

**Validates**: FR-019, FR-020, FR-022 — determinism and frequency increment.

```bash
# Run V-004 first, then:
curl -X POST http://localhost:8000/tokenize/text \
  -F "text=Hello world!" \
  -F "tokenizer=custom"
```

**Expected**:
- HTTP 200
- `new_token_ids` is empty list `[]`
- All vocabulary entries have `is_new: false`
- `frequency` values are 2 (incremented from first call)
- Token IDs are identical to V-004 (determinism)

---

### V-006: Custom Tokenizer Reset

**Validates**: FR-030, SC-005.

```bash
curl -X POST http://localhost:8000/tokenize/custom/reset
```

**Expected**:
- HTTP 200
- `{ "message": "Custom tokenizer vocabulary has been reset." }`

```bash
# Immediately after reset, tokenize again:
curl -X POST http://localhost:8000/tokenize/text \
  -F "text=Hello world!" \
  -F "tokenizer=custom"
```

**Expected**: All tokens are `is_new: true` again; frequencies are back to 1.

---

### V-007: TXT File Upload

**Validates**: FR-002, FR-004, FR-009.

```bash
echo "The quick brown fox jumps over the lazy dog." > /tmp/test.txt
curl -X POST http://localhost:8000/tokenize/file \
  -F "file=@/tmp/test.txt;type=text/plain" \
  -F "tokenizer=tiktoken" \
  -F "encoding=cl100k_base"
```

**Expected**:
- HTTP 200
- `source_type` = `"txt"`
- `original_text` = `"The quick brown fox jumps over the lazy dog."`
- `token_count` > 0

---

### V-008: PDF File Upload

**Validates**: FR-003, FR-006, FR-009.

```bash
# Use any text-based PDF
curl -X POST http://localhost:8000/tokenize/file \
  -F "file=@/path/to/text_based.pdf;type=application/pdf" \
  -F "tokenizer=tiktoken" \
  -F "encoding=cl100k_base"
```

**Expected**:
- HTTP 200
- `source_type` = `"pdf"`
- `original_text` contains extracted PDF text
- `token_count` > 0

---

### V-009: Validation — Empty Text

**Validates**: FR-031, SC-004.

```bash
curl -X POST http://localhost:8000/tokenize/text \
  -F "text=   " \
  -F "tokenizer=tiktoken" \
  -F "encoding=cl100k_base"
```

**Expected**: HTTP 400, `{ "detail": "Input text cannot be empty." }`

---

### V-010: Validation — Unsupported File Type

**Validates**: FR-004, SC-004.

```bash
echo "test" > /tmp/test.docx
curl -X POST http://localhost:8000/tokenize/file \
  -F "file=@/tmp/test.docx" \
  -F "tokenizer=tiktoken" \
  -F "encoding=cl100k_base"
```

**Expected**: HTTP 400, detail mentions supported file types (.txt, .pdf).

---

### V-011: Validation — Unsupported Encoding

**Validates**: FR-012, SC-004.

```bash
curl -X POST http://localhost:8000/tokenize/text \
  -F "text=hello" \
  -F "tokenizer=tiktoken" \
  -F "encoding=gpt2"
```

**Expected**: HTTP 400, detail mentions `gpt2` is unsupported.

---

### V-012: UI — Full Flow (manual browser check)

**Validates**: FR-035, SC-001, SC-007, SC-008.

1. Open `http://localhost:5173` in browser.
2. Confirm visible: title, description, input mode selector, text area, tokenizer mode toggle, encoding selector, Tokenize button.
3. Type `"Hello world!"` in text area.
4. Select **Tiktoken** mode, choose `cl100k_base`.
5. Click **Tokenize**.
6. Confirm: loading indicator appears, then token table with 3+ rows, statistics panel with all 5 metrics.
7. Switch to **Custom** mode, click **Tokenize**.
8. Confirm: vocabulary panel appears, all tokens marked as NEW (neon green).
9. Click **Tokenize** again (same text).
10. Confirm: all tokens marked as EXISTING (violet), frequencies = 2.
11. Click **Reset Vocabulary**.
12. Confirm: vocabulary panel clears.
13. Upload a `.txt` file.
14. Confirm: extracted text section appears, tokenization succeeds.

---

## Expected Directory Structure After Setup

```text
tokenizer-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   ├── tiktoken_service.py
│   │   │   ├── custom_tokenizer_service.py
│   │   │   ├── file_processor.py
│   │   │   └── statistics.py
│   │   └── routes/
│   │       └── tokenize.py
│   ├── tests/
│   │   ├── test_tiktoken_service.py
│   │   ├── test_custom_tokenizer_service.py
│   │   ├── test_file_processor.py
│   │   └── test_routes.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── types/
    │   │   └── api.ts
    │   ├── services/
    │   │   └── api.ts
    │   ├── components/
    │   │   ├── InputPanel.tsx
    │   │   ├── TokenizerControls.tsx
    │   │   ├── StatisticsPanel.tsx
    │   │   ├── TokenTable.tsx
    │   │   ├── VocabularyPanel.tsx
    │   │   ├── ExtractedTextPanel.tsx
    │   │   └── ErrorMessage.tsx
    │   └── styles/
    │       └── index.css
    ├── tests/
    │   └── *.test.tsx
    └── package.json
```
