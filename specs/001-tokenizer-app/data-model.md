# Data Model: Tokenizer Application

**Feature**: 001-tokenizer-app
**Date**: 2026-09-27
**Source**: spec.md → Key Entities + FR-001–FR-035, research.md D-005 / D-008

---

## Entities

### 1. TokenizationRequest

Represents a single tokenization call from the frontend to the backend.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `source_type` | enum: `text \| txt \| pdf` | required | Discriminates processing path |
| `text` | string \| null | non-empty if source_type=text | Raw user text |
| `file` | bytes \| null | ≤10 MB; .txt or .pdf | File payload (multipart) |
| `tokenizer` | enum: `tiktoken \| custom` | required | Selects service |
| `encoding` | string \| null | required if tokenizer=tiktoken | e.g. `cl100k_base` |

**Validation rules**:
- `text` MUST be non-empty string when `source_type == "text"`
- `file` MUST be provided when `source_type` is `"txt"` or `"pdf"`
- `encoding` MUST be one of the supported Tiktoken encodings when `tokenizer == "tiktoken"`
- `file` MIME type MUST match source_type (text/plain → txt, application/pdf → pdf)
- `file` size MUST NOT exceed `MAX_UPLOAD_BYTES` (default 10 MB)

---

### 2. Token

A single tokenization unit within a result. Immutable once produced.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `index` | int | ≥0, 0-based | Position in token sequence |
| `token_id` | int | ≥0 | Tiktoken: library-assigned; Custom: vocabulary-assigned |
| `token_text` | string | non-empty | Decoded text; hex-escaped if not valid UTF-8 |

---

### 3. TokenizationResult

The complete response returned by the backend for any successful tokenization.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `original_text` | string | non-empty | The text that was tokenized |
| `source_type` | enum: `text \| txt \| pdf` | required | Echoed from request |
| `tokenizer` | enum: `tiktoken \| custom` | required | Echoed from request |
| `encoding` | string | required | Tiktoken: actual encoding name; Custom: `"custom"` |
| `token_count` | int | ≥0 | Length of `tokens` list |
| `tokens` | Token[] | length = token_count | Ordered list of Token objects |
| `token_ids` | int[] | length = token_count | Extracted from tokens for convenience |
| `token_texts` | string[] | length = token_count | Extracted from tokens for convenience |
| `char_count` | int | ≥0 | `len(original_text)` |
| `word_count` | int | ≥0 | `len(original_text.split())` |
| `tokens_per_word` | float | ≥0.0 | 0.0 if word_count == 0 |
| `tokens_per_char` | float | ≥0.0 | 0.0 if char_count == 0 |
| `vocabulary` | VocabularyEntry[] \| null | present only if tokenizer=custom | Current full vocabulary snapshot |
| `new_token_ids` | int[] \| null | present only if tokenizer=custom | IDs of tokens new in this call |

---

### 4. VocabularyEntry

A record in the Custom Tokenizer's in-memory vocabulary. Mutated on each tokenization call.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `token_id` | int | ≥0, unique, stable | Assigned once, never changes |
| `token_text` | string | non-empty, unique key | Token string as split by regex |
| `frequency` | int | ≥1 | Cumulative count across all tokenization calls |
| `is_new` | bool | context-dependent | True only in the response for the call that created this entry |

**State transitions**:
- `CREATED`: First time a token text is seen → entry created, `frequency=1`, `is_new=True`
- `SEEN_AGAIN`: Token text seen in subsequent call → `frequency += occurrences_in_call`, `is_new=False`
- `RESET`: User calls reset endpoint → all entries deleted, counter reset to 0

---

### 5. VocabularyState (internal service state, not serialized)

| Field | Type | Notes |
|-------|------|-------|
| `entries` | dict[str, VocabularyEntry] | Keyed by token_text |
| `next_id` | int | Monotonically incrementing counter starting at 0 |

**Invariants**:
- `token_id` values are dense integers starting at 0 assigned in order of first appearance
- No two entries share the same `token_id` or `token_text`
- `frequency` is always ≥ 1 for any entry that exists in the vocabulary

---

### 6. ErrorResponse

Returned by all error paths. Consistent structure across all endpoints.

| Field | Type | Notes |
|-------|------|-------|
| `detail` | string | Human-readable error message, safe to display in UI |

HTTP status codes used:
- `400` — Client error (empty input, bad file type, corrupt PDF, no extractable text, unsupported encoding)
- `413` — File too large
- `422` — Pydantic validation error (malformed request body)
- `500` — Unexpected server error (generic fallback)

---

## State Transitions Diagram

```
CustomTokenizerService lifecycle:

  [init]
    |
    v
  EMPTY (next_id=0, entries={})
    |
    | tokenize(text) called
    v
  ACTIVE (entries populated, next_id advances)
    |
    | tokenize(text) called again (some tokens new, some existing)
    v
  ACTIVE (entries grow or frequencies increment)
    |
    | reset() called
    v
  EMPTY (next_id=0, entries={})
```

---

## Supported Tiktoken Encodings (fixed list)

| Encoding Name | Model Family |
|--------------|--------------|
| `cl100k_base` | GPT-4, GPT-3.5-turbo, text-embedding-ada-002 |
| `p50k_base` | Codex, text-davinci-002/003 |
| `p50k_edit` | text-davinci-edit-001 |
| `r50k_base` | GPT-3 (davinci, curie, babbage, ada) |
| `o200k_base` | GPT-4o family |
