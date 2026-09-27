# TokenLab — Interactive Tokenizer & Token Analysis Platform

A full-stack web application for visualizing and analyzing text tokenization using OpenAI's `tiktoken` library and a custom deterministic tokenizer with dynamic vocabulary management.

TokenLab provides an interactive interface for exploring token IDs, token text, tokenizer modes, encoding differences, vocabulary information, statistics, and file-based tokenization.

---

## ✨ Features

- Interactive text tokenization
- Tiktoken-based tokenization
- Custom deterministic tokenizer
- Tiktoken encoding selection
- Token ID visualization
- Token text visualization
- Token statistics
- Dynamic custom vocabulary management
- File tokenization
- Extracted text display
- Tokenization error handling
- REST API backend
- Automated backend and frontend tests
- Cyberpunk dark UI with neon-gradient accents and glassmorphism

---

## 🧠 Tokenizer Modes

### Tiktoken

Uses the Python `tiktoken` library to generate token IDs and token text.

Supported encodings include:

- `cl100k_base`
- `o200k_base`

The encoding is important because the same text can produce different token IDs with different encodings.

For example:

```text
Input:
hello world

cl100k_base:
[15339, 1917]

o200k_base:
[24912, 2375]
```

These values are generated directly by the selected Tiktoken encoding.

### Custom Tokenizer

TokenLab also includes a deterministic custom tokenizer with dynamic vocabulary management.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │      React Frontend     │
                    │    TypeScript + Vite    │
                    └────────────┬────────────┘
                                 │
                                 │ REST API
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Backend    │
                    │         Python          │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
               ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │   Tiktoken   │  │    Custom    │  │     File     │
        │   Service    │  │   Tokenizer  │  │   Processor  │
        └──────────────┘  └──────────────┘  └──────────────┘
               │                 │
               ▼                 ▼
          Token IDs &       Dynamic Vocabulary
          Token Text
```

---

## 🛠️ Tech Stack

### Frontend

- React 18
- TypeScript
- Vite
- Vitest
- React Testing Library
- CSS

### Backend

- Python 3.11+
- FastAPI
- Pydantic v2
- Tiktoken
- PyMuPDF
- Pytest

### Development

- Git
- REST API
- Component-based architecture
- Automated testing

---

## 📁 Project Structure

```text
TokenLab/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── tokenize.py
│   │   │
│   │   ├── services/
│   │   │   ├── custom_tokenizer_service.py
│   │   │   ├── file_processor.py
│   │   │   ├── statistics.py
│   │   │   └── tiktoken_service.py
│   │   │
│   │   ├── config.py
│   │   ├── schemas.py
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── tests/
│   │   └── types/
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── specs/
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

Install:

- Python 3.11+
- Node.js
- npm
- Git

### Backend

Open PowerShell and run:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

### Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/tokenize/encodings` | Get available Tiktoken encodings |
| POST | `/tokenize/text` | Tokenize submitted text |
| POST | `/tokenize/file` | Tokenize an uploaded file |
| POST | `/tokenize/custom/reset` | Reset custom tokenizer vocabulary |

---

## 🧪 Testing

### Backend

```powershell
cd backend
pytest
```

### Frontend

```powershell
cd frontend
npm run test
```

The project contains tests for tokenizer services, file processing, statistics, API routes, and React components.

---

## 📋 Validation

End-to-end validation scenarios are documented in:

```text
specs/001-tokenizer-app/quickstart.md
```

The project includes validation scenarios V-001 through V-012.

---

## 🔮 Future Enhancements

Possible future improvements:

- Additional tokenizer encodings
- Token frequency visualization
- Token distribution charts
- Side-by-side encoding comparison
- Token cost estimation
- Additional file formats
- Tokenization history
- Exportable tokenization reports
- Production deployment

---

## 👨‍💻 Author

**Rohith Kappara**

GitHub: [kapparaRohith](https://github.com/kapparaRohith)

---

⭐ If you find TokenLab useful, consider giving the repository a star.
