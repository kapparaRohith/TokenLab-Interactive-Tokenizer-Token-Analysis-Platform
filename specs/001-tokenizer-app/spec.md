# Feature Specification: Tokenizer Application

**Feature Branch**: `001-tokenizer-app`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "A small, clean tokenizer application focused on understanding how text is converted into tokens, supporting Tiktoken and a Custom Tokenizer with vocabulary management."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Direct Text Tokenization (Priority: P1)

A user types or pastes text directly into the input area, selects a tokenizer mode (Tiktoken
or Custom), optionally selects an encoding (for Tiktoken), and clicks Tokenize. The
application displays a token table with index, token ID, and decoded token text, along with
statistics (character count, word count, token count, tokens-per-word, tokens-per-character).

**Why this priority**: This is the fundamental use case the application exists to serve. Every
other story builds on this capability.

**Independent Test**: Can be fully tested by entering text, clicking Tokenize, and verifying
the token table and statistics panel are populated correctly.

**Acceptance Scenarios**:

1. **Given** the user enters valid text and selects Tiktoken mode with a valid encoding,
   **When** they click Tokenize,
   **Then** the token table displays one row per token with correct index, real Tiktoken token
   ID, and decoded text; and the statistics section shows accurate character count, word count,
   token count, tokens-per-word, and tokens-per-character values.

2. **Given** the user enters valid text and selects Custom Tokenizer mode,
   **When** they click Tokenize,
   **Then** the token table displays one row per token with deterministic token IDs from the
   custom vocabulary; the vocabulary panel updates immediately to reflect new or existing entries.

3. **Given** the input field is empty,
   **When** the user clicks Tokenize,
   **Then** a clear validation error is displayed and no tokenization request is made.

---

### User Story 2 — TXT File Upload & Tokenization (Priority: P2)

A user uploads a `.txt` file. The application extracts the file's text content in the
backend, displays the extracted text, and allows the user to tokenize it with any supported
tokenizer mode.

**Why this priority**: File-based input is a natural extension of direct text entry and is
needed for processing larger or pre-existing content.

**Independent Test**: Can be fully tested by uploading a valid `.txt` file and verifying the
extracted text section appears and tokenization proceeds correctly.

**Acceptance Scenarios**:

1. **Given** the user selects TXT upload mode and uploads a valid `.txt` file,
   **When** the application processes the file,
   **Then** the extracted text is shown in the "Extracted Text" section and the Tokenize
   button becomes available.

2. **Given** the user uploads a file with an unsupported extension (e.g., `.docx`),
   **When** the backend validates the file type,
   **Then** a user-friendly error message is displayed explaining the supported file types,
   and no tokenization is attempted.

3. **Given** the user uploads an oversized file (exceeding the backend size limit),
   **When** the backend validates the file size,
   **Then** a user-friendly error message is displayed stating the size limit, and the file
   is rejected before any processing occurs.

---

### User Story 3 — PDF File Upload & Text Extraction (Priority: P2)

A user uploads a text-based PDF. The backend extracts readable text from the PDF and
displays it, enabling subsequent tokenization.

**Why this priority**: PDF is a common document format; supporting it extends the
application's practical utility significantly.

**Independent Test**: Can be fully tested by uploading a valid text-based PDF and verifying
the extracted text appears correctly in the UI.

**Acceptance Scenarios**:

1. **Given** the user selects PDF upload mode and uploads a valid text-based PDF,
   **When** the backend extracts text,
   **Then** the extracted text is displayed in the "Extracted Text" section and is available
   for tokenization.

2. **Given** the user uploads a corrupted or unreadable PDF,
   **When** the backend attempts extraction,
   **Then** a user-friendly error message is displayed and no empty or garbage text is shown.

3. **Given** the user uploads a PDF with no extractable text (e.g., a scanned image-only PDF
   without OCR data),
   **When** the backend attempts extraction,
   **Then** a user-friendly error message is displayed explaining that no text could be
   extracted, distinguishing this from a corrupted file.

---

### User Story 4 — Tiktoken Encoding Selection (Priority: P2)

When Tiktoken mode is selected, the user can choose from a list of supported encodings
(e.g., cl100k_base, p50k_base). The selected encoding governs the tokenization and is
reflected in the API response.

**Why this priority**: Encoding selection is central to Tiktoken's value; without it, users
cannot explore how different models tokenize text.

**Independent Test**: Can be tested by switching encodings and verifying that the same input
produces different token counts and IDs for different encodings.

**Acceptance Scenarios**:

1. **Given** Tiktoken mode is selected,
   **When** the user opens the encoding selector,
   **Then** all supported encodings are listed and selectable.

2. **Given** the user selects a valid encoding and tokenizes text,
   **When** the response is returned,
   **Then** the selected encoding name is shown in the response and the token IDs correspond
   to that encoding's vocabulary.

3. **Given** an unsupported encoding identifier is submitted (e.g., via API manipulation),
   **When** the backend validates the request,
   **Then** a structured error response is returned with a clear message.

---

### User Story 5 — Token Results Visualization (Priority: P2)

After tokenization, the user sees a structured visualization of the tokenization result:
a table with token index, token ID, decoded token text, and any relevant additional
details. The statistics panel shows aggregate counts.

**Why this priority**: The visualization is what makes the application educational and
useful; raw API data alone does not fulfill the product goal.

**Independent Test**: Can be tested by checking that the token table has correct column
headers, one row per token, and that statistics match the actual token list.

**Acceptance Scenarios**:

1. **Given** a successful tokenization response,
   **When** the token table is rendered,
   **Then** each row displays: token index (0-based), token ID, and decoded token text;
   total rows equal the token count.

2. **Given** a successful tokenization response,
   **When** the statistics section is rendered,
   **Then** character count, word count, token count, tokens-per-word, and
   tokens-per-character are all displayed and mathematically consistent with the token list.

---

### User Story 6 — Custom Vocabulary Management (Priority: P3)

When Custom Tokenizer mode is used, the user can view the current in-memory vocabulary
(token ID, token text, frequency, status). Tokens newly created during the current
operation are visually distinguished from existing ones. The user can reset the
vocabulary to its initial state.

**Why this priority**: Vocabulary visibility is the key differentiator of the Custom
Tokenizer; it fulfills the educational goal of showing how a tokenizer builds its lexicon.

**Independent Test**: Can be tested independently by tokenizing novel text and verifying
the vocabulary panel shows new entries with a distinct visual style, then resetting and
confirming the vocabulary clears.

**Acceptance Scenarios**:

1. **Given** a successful custom tokenization,
   **When** the vocabulary panel is displayed,
   **Then** every token in the result has a corresponding vocabulary entry showing ID,
   token text, frequency, and status (new vs. existing).

2. **Given** the same token appears in multiple tokenization operations,
   **When** the vocabulary panel is displayed,
   **Then** the token's frequency reflects the cumulative count across all operations and
   its status is "existing" (not "new") after the first operation.

3. **Given** the user clicks the Reset Vocabulary button,
   **When** the reset is confirmed,
   **Then** the custom vocabulary is cleared to its initial state and the vocabulary panel
   reflects zero entries (or the initial seeded state, if any).

4. **Given** the same input is tokenized twice without resetting,
   **When** the second tokenization completes,
   **Then** no entries are marked "new" (all were seen in the first pass) and frequencies
   have incremented.

---

### User Story 7 — Input Validation & Error Handling (Priority: P1)

All invalid inputs (empty text, wrong file type, oversized file, corrupted PDF, image-only
PDF, unsupported encoding) produce clear, user-friendly error messages. The UI recovers
gracefully and allows the user to correct the input.

**Why this priority**: Without robust error handling the application is unreliable; users
must always know what went wrong and how to fix it.

**Independent Test**: Can be tested by submitting each invalid input type and verifying the
specific error message is shown and the application remains functional afterward.

**Acceptance Scenarios**:

1. **Given** the user submits empty text or no file,
   **When** Tokenize is clicked,
   **Then** a validation message "Input cannot be empty" (or equivalent) is shown; no
   network request is made.

2. **Given** the backend returns a structured error (e.g., unsupported file type),
   **When** the frontend receives the error,
   **Then** the human-readable error detail is displayed; the previous tokenization result
   (if any) is preserved or cleared consistently.

3. **Given** a processing error occurs (e.g., corrupted PDF),
   **When** the backend returns the error,
   **Then** the error message clearly describes the problem without exposing internal
   stack traces.

---

### User Story 8 — Responsive & Accessible Interface (Priority: P3)

The application is usable on common screen sizes (desktop and tablet). All interactive
controls have accessible labels, keyboard navigation is possible, and loading/empty/error
states are communicated clearly.

**Why this priority**: Accessibility and responsiveness are baseline quality expectations,
not optional enhancements.

**Independent Test**: Can be tested by resizing to tablet width and using keyboard-only
navigation through the full tokenization flow.

**Acceptance Scenarios**:

1. **Given** the user views the application on a tablet-width viewport (>=768px),
   **When** all elements are rendered,
   **Then** all controls, tables, and panels are readable and operable without horizontal
   scrolling.

2. **Given** the user navigates using only a keyboard,
   **When** moving through interactive controls,
   **Then** all buttons, selectors, file inputs, and text areas are reachable and
   operable via Tab and Enter/Space keys.

3. **Given** a tokenization request is in progress,
   **When** the UI is in loading state,
   **Then** a visible loading indicator is shown and the Tokenize button is disabled to
   prevent duplicate submissions.

---

### Edge Cases

- What happens when a PDF has mixed pages (some with text, some image-only)?
  -> Extract whatever text is available; if zero text is extracted total, return the
  "no extractable text" error.
- What happens when a TXT file contains only whitespace or newlines?
  -> Backend treats this as empty input and returns a validation error.
- What happens when the custom vocabulary grows very large within a session?
  -> The vocabulary panel displays all entries; no truncation is applied unless the
  session is reset or the backend is restarted.
- What happens when two tokens in the custom tokenizer have the same text?
  -> This cannot occur; token text is the uniqueness key for vocabulary entries.
- What happens when the selected Tiktoken encoding cannot decode a token back to text?
  -> The raw bytes representation is displayed for that token in the token text column.

---

## Requirements *(mandatory)*

### Functional Requirements

**Input**

- **FR-001**: The system MUST provide a text input area where users can type or paste text directly.
- **FR-002**: The system MUST provide a TXT file upload control that accepts `.txt` files.
- **FR-003**: The system MUST provide a PDF file upload control that accepts `.pdf` files.
- **FR-004**: The backend MUST validate the file type of any uploaded file before attempting to read or extract content.
- **FR-005**: The backend MUST validate that uploaded files do not exceed a maximum size limit before processing.
- **FR-006**: The backend MUST extract plain text from text-based PDF files.
- **FR-007**: The backend MUST return a structured error if a PDF is corrupted or unreadable.
- **FR-008**: The backend MUST return a structured error if a PDF contains no extractable text.
- **FR-009**: The frontend MUST display the extracted text from uploaded files in a dedicated "Extracted Text" section.

**Tokenizer Selection**

- **FR-010**: The system MUST provide a control to select between Tiktoken and Custom Tokenizer modes.
- **FR-011**: When Tiktoken mode is selected, the system MUST provide a control to select a supported Tiktoken encoding.
- **FR-012**: The backend MUST reject tokenization requests with an unsupported or unrecognized encoding with a structured error response.
- **FR-013**: Tiktoken vocabulary and token IDs MUST remain exactly as produced by the Tiktoken library; the application MUST NOT modify them.
- **FR-014**: Tiktoken and Custom Tokenizer behavior MUST be fully independent; a change to one MUST NOT affect the other.

**Tokenization**

- **FR-015**: The system MUST tokenize input using the selected tokenizer when the user clicks the Tokenize button.
- **FR-016**: The backend MUST return for every tokenization response: original text, token count, list of token IDs, list of decoded token texts, character count, word count, tokens-per-word, tokens-per-character, selected encoding (or tokenizer identifier), and source type (text/txt/pdf).
- **FR-017**: Tiktoken tokenization MUST use the actual selected encoding and return real token IDs as produced by that encoding.
- **FR-018**: Custom Tokenizer MUST use a deterministic token-splitting strategy that produces the same token sequence for identical input.
- **FR-019**: Custom Tokenizer MUST assign deterministic, stable token IDs: the same token string MUST always receive the same ID within a running session.
- **FR-020**: Custom Tokenizer MUST reuse existing vocabulary entries for previously seen tokens.
- **FR-021**: Custom Tokenizer MUST create new vocabulary entries with new IDs for tokens not yet in the vocabulary.
- **FR-022**: Custom Tokenizer MUST track and return the cumulative frequency of each token across all tokenization operations in the current session.
- **FR-023**: Custom Tokenizer MUST identify and flag tokens that are newly created during the current tokenization operation (not present in vocabulary before that call).

**Results Display**

- **FR-024**: The frontend MUST display a token table with at minimum the following columns: token index, token ID, and decoded token text.
- **FR-025**: The frontend MUST display a statistics panel showing character count, word count, token count, tokens-per-word, and tokens-per-character for each successful tokenization.
- **FR-026**: The frontend MUST update the token table and statistics panel immediately upon receiving a successful tokenization response.

**Custom Vocabulary Display**

- **FR-027**: When Custom Tokenizer mode is active, the frontend MUST display the current vocabulary with each entry showing: token ID, token text, cumulative frequency, and status (new / existing).
- **FR-028**: The frontend MUST visually distinguish newly created tokens from existing tokens in the vocabulary display (e.g., via color, badge, or icon).
- **FR-029**: The frontend MUST update the vocabulary display immediately after each successful custom tokenization.
- **FR-030**: The system MUST provide a Reset Vocabulary control. Activating it MUST restore the Custom Tokenizer vocabulary to its initial (empty or seeded) state.

**Validation & Error States**

- **FR-031**: The frontend MUST prevent submission of an empty input (text or file) and display a user-friendly validation message without making a network request.
- **FR-032**: The frontend MUST display all backend-returned error messages in a human-readable format, without exposing raw exception traces or internal error codes.
- **FR-033**: The system MUST provide clear loading, empty, error, and success states for the results area.

**Persistence**

- **FR-034**: The system MUST NOT persist vocabulary data, user input, or tokenization history to any database or durable storage.

**Interface Structure**

- **FR-035**: The frontend MUST include the following UI elements: application title, description, input mode selection, text input / file upload controls, encoding selector (visible when Tiktoken is selected), Tokenize button, statistics section, token visualization section, extracted text section (visible for file uploads), vocabulary panel (visible when Custom Tokenizer is selected), and error message area.

---

### Key Entities

- **TokenizationRequest**: Encapsulates input source (text, TXT file, PDF file), selected tokenizer mode, and selected encoding. Key attributes: source type, raw content or file reference, tokenizer mode, encoding identifier.

- **TokenizationResult**: The response produced by a tokenization operation. Key attributes: original text, token count, token ID list, decoded token text list, character count, word count, tokens-per-word, tokens-per-character, encoding used, source type.

- **Token**: A single tokenization unit within a result. Key attributes: index (0-based), token ID, decoded text.

- **VocabularyEntry** (Custom Tokenizer only): A record in the in-memory custom vocabulary. Key attributes: token ID (stable, deterministic integer), token text (unique key), cumulative frequency, creation status relative to current operation (new / existing).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a full tokenization cycle (enter text -> select tokenizer -> view results) in under 10 seconds on an average network connection.
- **SC-002**: All tokenization responses include every required field (original text, token count, token IDs, decoded tokens, character count, word count, tokens-per-word, tokens-per-character, encoding, source type) with no missing values.
- **SC-003**: The same input tokenized twice with the Custom Tokenizer produces identical token ID sequences in both operations (determinism guarantee is 100%).
- **SC-004**: All defined input validation scenarios (empty text, wrong file type, oversized file, corrupted PDF, image-only PDF, unsupported encoding) display a specific, human-readable error message, with zero generic or technical error surfaces.
- **SC-005**: After a vocabulary reset, the Custom Tokenizer vocabulary contains zero entries; the next tokenization operation populates it from scratch.
- **SC-006**: Tiktoken token IDs returned by the application match those produced directly by the Tiktoken library for the same input and encoding (100% fidelity).
- **SC-007**: The application is fully operable on viewport widths >= 768px without horizontal scrolling.
- **SC-008**: All interactive controls are reachable and operable via keyboard navigation only.

---

## Assumptions

- Users are operating modern browsers (Chrome, Firefox, Edge, current versions); Internet Explorer is not supported.
- PDF support covers text-based PDFs only; scanned/image PDFs requiring OCR are explicitly out of scope.
- File size limit for uploads is determined by the backend; a reasonable default (e.g., 10 MB) will be chosen during implementation.
- The supported Tiktoken encodings list is drawn from those available in the Tiktoken library at the time of implementation; it is a fixed list, not user-configurable.
- The Custom Tokenizer uses a simple whitespace- and punctuation-aware splitting strategy as its tokenization algorithm; the exact strategy is an implementation decision.
- The Custom Tokenizer vocabulary persists only for the lifetime of the backend process; restarting the backend resets it.
- No authentication, user accounts, sessions, or per-user vocabulary isolation is required.
- Mobile viewports below 768px are not a primary target for this version; responsive behavior at >=768px is required.
- The application is a standalone tool; no integration with external services (cloud storage, LLMs, etc.) is in scope.
- Token IDs assigned by the Custom Tokenizer start from 0 and increment sequentially; this is deterministic within a session.

---

## Out of Scope

The following are explicitly excluded and MUST NOT be introduced:

- Authentication, user accounts, or session management
- Database or any form of durable vocabulary/data persistence
- OCR for scanned PDFs
- Cloud storage or file persistence after processing
- LLM inference or model-based tokenization beyond Tiktoken and Custom Tokenizer
- Billing, quotas, or rate limiting
- Tokenizer training or vocabulary fine-tuning
- Any tokenizer beyond Tiktoken and the application's Custom Tokenizer
