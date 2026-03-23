# TalentLens — AI-Powered Resume Screening

> **Hire sharper. Decide faster.**

TalentLens is an intelligent resume screening tool built for HR professionals. Upload a job description and multiple resumes — TalentLens ranks candidates using a hybrid scoring system combining semantic similarity, skill matching, and LLM-based evaluation.


## Features

- **Multi-resume upload** — drag and drop multiple PDFs at once
- **Hybrid scoring** — semantic similarity (Sentence-BERT) + skill matching + AI evaluation (Groq LLaMA)
- **Smart skill extraction** — 500+ skills across 18 categories, synonym-aware
- **Section-aware parsing** — extracts experience, education, contact info from any resume format
- **Filter & sort** — filter by Strong / Moderate / Weak match or sort by score 
- **Clean HR-friendly UI** - Simple, clean interface with no technical complexity 



## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| PDF Extraction | pdfplumber, PyMuPDF |
| OCR Fallback | Tesseract + Pillow |
| NLP / NER | spaCy (en_core_web_sm) |
| Semantic Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| LLM Scoring | Groq API (LLaMA 3.3 70B) |
| Skill Taxonomy | Custom JSON — 500+ skills, 18 categories |

### Frontend
| Layer | Technology |
|---|---|
| UI | HTML + CSS + JavaScript |
| Styling | Bootstrap 5 + Custom CSS |
| Architecture | Single Page Application (SPA) |

---

## How It Works

```
PDF Resumes
     ↓
PDFReader → OCRReader (fallback for scanned PDFs)
     ↓
TextPreprocessor (soft clean → section detection)
     ↓
SectionExtractor → {experience, education, skills, contact}
     ↓
EntityExtractor  → name, email, phone
SkillExtractor   → matched skills from taxonomy
     ↓
EmbeddingService → semantic similarity score  (40%)
SkillExtractor   → skill match score          (40%)
Groq LLaMA       → AI holistic score          (20%)
     ↓
Weighted Final Score → Ranked candidates
```

---

## Scoring System

| Signal | Weight | Description |
|---|---|---|
| Semantic Similarity | 40% | How relevant is the candidate's background to the JD |
| Skill Match | 40% | What % of required skills are present in the resume |
| AI Evaluation | 20% | LLaMA's holistic judgment of candidate fit |

### Match Labels
| Score | Label |
|---|---|
| 75%+ | Strong Match |
| 55–74% | Moderate Match |
| Below 55% | Weak Match |

---

## Project Structure

```
resume-screening/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic request/response models
│   │   ├── routes/
│   │   │   ├── resume.py              # POST /resume/parse-multiple
│   │   │   ├── jd.py                  # POST /jd/parse
│   │   │   └── scoring.py             # POST /scoring/rank
│   │   └── services/
│   │       ├── parser/
│   │       │   ├── pdf_reader.py      # PDF text extraction
│   │       │   ├── ocr_reader.py      # OCR fallback
│   │       │   ├── preprocessor.py    # Text cleaning
│   │       │   ├── section_extractor.py
│   │       │   ├── entity_extractor.py
│   │       │   ├── skill_extractor.py
│   │       │   ├── pipeline.py        # Orchestrates parsing
│   │       │   └── data/
│   │       │       └── common_skills.json
│   │       ├── embedding_service.py   # Sentence-BERT embeddings
│   │       └── scorer.py             # Weighted scoring + Groq LLM
│   ├── .env
│   └── requirements.txt
│
└── frontend/
    ├── index.html
    ├── css/
    │   ├── base.css
    │   ├── components.css
    │   └── page.css
    └── js/
        ├── navigation.js
        ├── upload.js
        ├── api.js
        └── app.js
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/resume/parse` | Parse single resume PDF |
| `POST` | `/resume/parse-multiple` | Parse multiple resume PDFs |
| `POST` | `/jd/parse` | Extract skills from job description |
| `POST` | `/scoring/rank` | Score and rank candidates against JD |

Full interactive docs available at `/docs` when running locally.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Tesseract OCR installed ([Windows guide](https://github.com/UB-Mannheim/tesseract/wiki))
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/resume-screening.git
cd resume-screening/backend

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the backend
uvicorn app.main:app --reload
```

### Run Frontend

Open `frontend/index.html` directly in your browser, or use Live Server in VS Code.

Make sure backend is running on `http://localhost:8000`.

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```
GROQ_API_KEY=your_groq_api_key_here
```

## Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [Groq](https://groq.com/)
- [spaCy](https://spacy.io/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [Bootstrap 5](https://getbootstrap.com/)

## Demo Video

[Watch Demo](https://www.loom.com/share/ce5242a0aa314cea836ceb7aa72792e9)
