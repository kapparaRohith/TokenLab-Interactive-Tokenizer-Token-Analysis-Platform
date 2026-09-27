# Tokenizer Application

A modern, interactive web application to visualize text tokenization using authoritative OpenAI Tiktoken encodings and a custom deterministic tokenizer with dynamic vocabulary management.

## Project Architecture

- **Backend**: FastAPI (Python 3.11+), Pydantic v2, Tiktoken, PyMuPDF, pytest.
- **Frontend**: React 18, TypeScript, Vite, Vitest, React Testing Library.
- **Styling**: Cyberpunk Dark Mode with Neon-Gradient Accents & Glassmorphism design system.

---

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend will start at `http://localhost:8000`. API Documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will start at `http://localhost:5173`.

---

## Running Tests

### Backend Tests (pytest)

```bash
cd backend
pytest
```

### Frontend Tests (Vitest)

```bash
cd frontend
npm run test
```

---

## End-to-End Validation Scenarios

See `specs/001-tokenizer-app/quickstart.md` for complete cURL and UI validation scenarios (V-001 through V-012).
