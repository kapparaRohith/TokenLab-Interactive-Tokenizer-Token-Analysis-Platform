# API Contract: Tokenizer Application REST API

**Version**: 1.0.0
**Base URL (dev)**: `http://localhost:8000`
**Content-Type**: All requests use `multipart/form-data`. All responses are `application/json`.
**CORS**: Configured for `http://localhost:5173` (Vite dev server) in development.

---

## Endpoints

### GET /health

**Purpose**: Health check — confirms the backend is running.

**Request**: No body, no parameters.

**Response 200**:
```json
{ "status": "ok" }
```

---

### GET /tokenize/encodings

**Purpose**: Returns the list of supported Tiktoken encoding names.

**Request**: No body, no parameters.

**Response 200**:
```json
{
  "encodings": [
    "cl100k_base",
    "p50k_base",
    "p50k_edit",
    "r50k_base",
    "o200k_base"
  ]
}
```

---

### POST /tokenize/text

**Purpose**: Tokenize a plain text string using Tiktoken or Custom Tokenizer.

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | yes | The text to tokenize. Must be non-empty after stripping. |
| `tokenizer` | string | yes | `"tiktoken"` or `"custom"` |
| `encoding` | string | conditional | Required when tokenizer=tiktoken. One of the supported encoding names. |

**Response 200** — `TokenizationResult`:
```json
{
  "original_text": "Hello world!",
  "source_type": "text",
  "tokenizer": "tiktoken",
  "encoding": "cl100k_base",
  "token_count": 3,
  "tokens": [
    { "index": 0, "token_id": 9906, "token_text": "Hello" },
    { "index": 1, "token_id": 1917, "token_text": " world" },
    { "index": 2, "token_id": 0, "token_text": "!" }
  ],
  "token_ids": [9906, 1917, 0],
  "token_texts": ["Hello", " world", "!"],
  "char_count": 12,
  "word_count": 2,
  "tokens_per_word": 1.5,
  "tokens_per_char": 0.25,
  "vocabulary": null,
  "new_token_ids": null
}
```

**Custom Tokenizer response adds**:
```json
{
  "tokenizer": "custom",
  "encoding": "custom",
  "vocabulary": [
    { "token_id": 0, "token_text": "Hello", "frequency": 1, "is_new": true },
    { "token_id": 1, "token_text": " world", "frequency": 1, "is_new": true },
    { "token_id": 2, "token_text": "!", "frequency": 1, "is_new": true }
  ],
  "new_token_ids": [0, 1, 2]
}
```

**Error responses**:

| Status | Condition | Detail example |
|--------|-----------|----------------|
| 400 | Empty or whitespace-only text | `"Input text cannot be empty."` |
| 400 | Unsupported encoding | `"Unsupported encoding: 'gpt2'. Supported: cl100k_base, ..."` |
| 422 | Missing required field | Pydantic validation detail |

---

### POST /tokenize/file

**Purpose**: Upload a TXT or PDF file, extract text, and tokenize it.

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | yes | `.txt` or `.pdf` file. Max 10 MB. |
| `tokenizer` | string | yes | `"tiktoken"` or `"custom"` |
| `encoding` | string | conditional | Required when tokenizer=tiktoken. |

**Response 200** — Same `TokenizationResult` shape as `/tokenize/text`, with:
- `source_type`: `"txt"` or `"pdf"` (detected from file extension / MIME type)
- `original_text`: the extracted text content

**Error responses**:

| Status | Condition | Detail example |
|--------|-----------|----------------|
| 400 | Unsupported file type | `"Unsupported file type. Only .txt and .pdf files are accepted."` |
| 400 | Corrupt/unreadable PDF | `"PDF is corrupted or unreadable."` |
| 400 | No extractable text in PDF | `"No extractable text found in PDF. The file may contain only images."` |
| 400 | Empty TXT file | `"The uploaded file contains no text content."` |
| 400 | Unsupported encoding | `"Unsupported encoding: 'gpt2'. Supported: cl100k_base, ..."` |
| 413 | File exceeds size limit | `"File too large. Maximum allowed size is 10 MB."` |
| 422 | Missing required field | Pydantic validation detail |

---

### POST /tokenize/custom/reset

**Purpose**: Reset the Custom Tokenizer vocabulary to its initial empty state.

**Request**: No body required.

**Response 200**:
```json
{ "message": "Custom tokenizer vocabulary has been reset." }
```

**Notes**: This endpoint affects global in-memory state. After reset, the next
`/tokenize/text` or `/tokenize/file` with `tokenizer=custom` will treat all tokens
as new.

---

## Pydantic Schemas (Backend — Python)

```python
# schemas.py

from enum import Enum
from pydantic import BaseModel


class TokenizerMode(str, Enum):
    tiktoken = "tiktoken"
    custom = "custom"


class SourceType(str, Enum):
    text = "text"
    txt = "txt"
    pdf = "pdf"


class TokenSchema(BaseModel):
    index: int
    token_id: int
    token_text: str


class VocabularyEntrySchema(BaseModel):
    token_id: int
    token_text: str
    frequency: int
    is_new: bool


class TokenizationResultSchema(BaseModel):
    original_text: str
    source_type: SourceType
    tokenizer: TokenizerMode
    encoding: str
    token_count: int
    tokens: list[TokenSchema]
    token_ids: list[int]
    token_texts: list[str]
    char_count: int
    word_count: int
    tokens_per_word: float
    tokens_per_char: float
    vocabulary: list[VocabularyEntrySchema] | None = None
    new_token_ids: list[int] | None = None


class EncodingsResponseSchema(BaseModel):
    encodings: list[str]


class ResetResponseSchema(BaseModel):
    message: str


class HealthResponseSchema(BaseModel):
    status: str
```

---

## TypeScript Interface Definitions (Frontend)

```typescript
// types/api.ts

export type TokenizerMode = 'tiktoken' | 'custom';
export type SourceType = 'text' | 'txt' | 'pdf';

export interface Token {
  index: number;
  token_id: number;
  token_text: string;
}

export interface VocabularyEntry {
  token_id: number;
  token_text: string;
  frequency: number;
  is_new: boolean;
}

export interface TokenizationResult {
  original_text: string;
  source_type: SourceType;
  tokenizer: TokenizerMode;
  encoding: string;
  token_count: number;
  tokens: Token[];
  token_ids: number[];
  token_texts: string[];
  char_count: number;
  word_count: number;
  tokens_per_word: number;
  tokens_per_char: number;
  vocabulary: VocabularyEntry[] | null;
  new_token_ids: number[] | null;
}

export interface EncodingsResponse {
  encodings: string[];
}

export interface ResetResponse {
  message: string;
}

export interface ApiError {
  detail: string;
}
```
