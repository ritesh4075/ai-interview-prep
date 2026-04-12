# 🎯 AI Interview Preparation Platform

> An intelligent, full-stack interview preparation system powered by NLP, LLMs, and real-time AI feedback — built for Data Science portfolios.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=flat-square&logo=openai)
![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=flat-square)

---

## 📌 Overview

This platform solves a real problem: students prepare for interviews randomly, with no structured feedback. This system provides:

- **AI-generated questions** tailored to your resume and target company
- **NLP-powered answer evaluation** (clarity, keywords, semantic similarity)
- **Voice analysis** for tone, pace, and confidence detection
- **Progress analytics** with personalized weak-area recommendations
- **Company-specific prep** (TCS, Amazon, Google, Infosys, Microsoft)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  React Frontend                      │
│   Dashboard | Mock Interview | Feedback | Analytics  │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│              Flask Backend (Python)                  │
│   Auth API | Interview API | Resume API | Progress   │
└──────┬───────────────┬───────────────┬──────────────┘
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────────────┐
│  AI / NLP   │ │  PostgreSQL │ │   Redis Cache       │
│  Services   │ │  Database   │ │   + Celery Queue    │
└─────────────┘ └─────────────┘ └────────────────────┘
```

---

## 🧠 Data Science Components

| Module | Technology | Purpose |
|--------|-----------|---------|
| Question Generator | OpenAI GPT-4 + LangChain | Resume-aware question generation |
| Answer Evaluator | sentence-transformers, spaCy | Semantic similarity + keyword scoring |
| Resume Parser | spaCy NER, PyPDF2 | Entity extraction from PDFs |
| Voice Analyzer | Whisper, librosa | Speech rate, filler word detection |
| Feedback Scorer | XGBoost, scikit-learn | Multi-feature interview score prediction |
| Recommendation Engine | scikit-learn (KNN) | Personalized topic suggestions |
| Progress Analytics | Pandas, Matplotlib | Historical trend analysis |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15
- Redis

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/ai-interview-prep.git
cd ai-interview-prep
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)
```

### 4. Database Setup

```bash
createdb interview_prep_db
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Frontend Setup

```bash
cd ../frontend
npm install
cp .env.example .env.local
```

### 6. Run Everything

```bash
# Terminal 1 — Backend
cd backend && flask run

# Terminal 2 — Frontend
cd frontend && npm run dev

# Terminal 3 — Redis (if installed locally)
redis-server
```

Visit: `http://localhost:5173`

---

## ⚙️ Configuration (.env)

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://localhost/interview_prep_db

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-jwt-secret

# AWS S3 (for resume storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=interview-prep-resumes
```

---

## 📁 Project Structure

```
ai-interview-prep/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── config.py               # Configuration
│   ├── requirements.txt
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── interview.py        # Interview session model
│   │   ├── response.py         # Answer response model
│   │   └── feedback.py         # AI feedback model
│   ├── routes/
│   │   ├── auth.py             # Login, signup, JWT
│   │   ├── interview.py        # Start/end sessions
│   │   ├── resume.py           # Upload & parse
│   │   └── feedback.py         # Get AI feedback
│   ├── services/
│   │   ├── question_generator.py   # LLM question generation
│   │   ├── answer_evaluator.py     # NLP evaluation
│   │   ├── resume_parser.py        # Resume NER
│   │   ├── voice_analyzer.py       # Audio processing
│   │   └── feedback_scorer.py      # ML scoring model
│   └── utils/
│       ├── auth_helpers.py
│       └── response_helpers.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Interview.jsx
│   │   │   └── Analytics.jsx
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   ├── interview/
│   │   │   ├── feedback/
│   │   │   └── dashboard/
│   │   └── hooks/
│   │       ├── useInterview.js
│   │       └── useAuth.js
├── notebooks/
│   ├── 01_resume_parsing_demo.ipynb
│   ├── 02_answer_evaluation.ipynb
│   ├── 03_feedback_model_training.ipynb
│   └── 04_recommendation_engine.ipynb
├── data/
│   └── question_banks/
│       ├── tcs.json
│       ├── amazon.json
│       └── google.json
├── docs/
│   └── architecture.md
└── scripts/
    └── seed_db.py
```

---

## 🔬 Notebooks

The `notebooks/` folder contains Jupyter notebooks demonstrating all DS components:

- `01_resume_parsing_demo.ipynb` — NER extraction walkthrough
- `02_answer_evaluation.ipynb` — semantic similarity scoring
- `03_feedback_model_training.ipynb` — XGBoost model training
- `04_recommendation_engine.ipynb` — KNN recommendation system

---

## 🛣️ Roadmap

- [x] Core Flask API
- [x] JWT Authentication
- [x] Resume Parser (spaCy NER)
- [x] LLM Question Generator
- [x] NLP Answer Evaluator
- [x] Feedback Scoring Model
- [ ] Voice Analysis (Whisper)
- [ ] Company-specific question banks
- [ ] Recommendation Engine
- [ ] Subscription billing (Razorpay)
- [ ] Mobile App (React Native)

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 👤 Author

Built as a Data Science portfolio project demonstrating end-to-end AI system design, NLP pipelines, and full-stack development.
