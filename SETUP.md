# ⚙️ Complete Setup Guide — AI Interview Prep Platform

Follow these steps exactly. Estimated time: 30–45 minutes.

---

## Step 1 — Install Prerequisites

### Python 3.10+
```bash
# Check your version first
python --version

# If not installed:
# Windows: https://python.org/downloads
# Ubuntu/Mac:
sudo apt install python3.10 python3.10-venv   # Ubuntu
brew install python@3.10                       # Mac
```

### Node.js 18+
```bash
node --version   # Check

# If not installed: https://nodejs.org (LTS version)
```

### PostgreSQL
```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib
sudo service postgresql start

# Mac
brew install postgresql
brew services start postgresql

# Windows: https://postgresql.org/download/windows
```

### Redis (optional for Phase 1 — skip if just testing)
```bash
# Ubuntu
sudo apt install redis-server
sudo service redis start

# Mac
brew install redis
brew services start redis

# Windows: https://github.com/microsoftproject/redis/releases
```

---

## Step 2 — Clone / Create the Project

```bash
# If cloning from GitHub:
git clone https://github.com/yourusername/ai-interview-prep.git
cd ai-interview-prep

# OR if using this code directly:
# Just make sure you're in the ai-interview-prep/ folder
```

---

## Step 3 — Setup PostgreSQL Database

```bash
# Open PostgreSQL shell
psql -U postgres

# Inside psql, run:
CREATE DATABASE interview_prep_db;
CREATE USER interview_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE interview_prep_db TO interview_user;
\q
```

---

## Step 4 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# Install dependencies (takes 3–5 min)
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Create your .env file
```bash
cp .env.example .env
```

Now open `backend/.env` in any text editor and fill in:
```
SECRET_KEY=any-random-string-like-abc123xyz
DATABASE_URL=postgresql://postgres:yourpassword@localhost/interview_prep_db
OPENAI_API_KEY=sk-your-key-from-openai.com
JWT_SECRET_KEY=another-random-string
```

> **Getting OpenAI API Key:**
> 1. Go to https://platform.openai.com/api-keys
> 2. Create account → Add billing (minimum $5)
> 3. Click "Create new secret key" → Copy it into .env

### Initialize database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Run the backend
```bash
flask run
# Should see: Running on http://127.0.0.1:5000
```

### Test backend is working
```bash
curl http://localhost:5000/api/health
# Expected: {"message":"AI Interview Prep API running","status":"ok"}
```

---

## Step 5 — Frontend Setup

Open a NEW terminal window (keep backend running):

```bash
cd frontend
npm install          # Takes 1–2 minutes
```

### Run the frontend
```bash
npm run dev
# Should see: Local: http://localhost:5173
```

Open browser: **http://localhost:5173** ✅

---

## Step 6 — Train the ML Model (Optional but Recommended)

```bash
# In your backend folder with venv activated:
pip install jupyter
jupyter notebook

# Open: notebooks/03_feedback_model_training.ipynb
# Run all cells — saves model to data/feedback_model.pkl
```

---

## Step 7 — Test the Full Flow

1. Go to http://localhost:5173
2. Click "Sign Up" → Create account
3. Upload a PDF resume
4. Set company to "Amazon", difficulty to "medium"
5. Click "Start Interview"
6. Answer the AI-generated questions
7. View your feedback scores

---

## Common Errors & Fixes

### "psycopg2 installation failed"
```bash
# Ubuntu
sudo apt install libpq-dev python3-dev
pip install psycopg2-binary

# Mac
brew install postgresql
pip install psycopg2-binary
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
# If that fails:
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz
```

### "OpenAI API key invalid"
- Check there are no spaces in your .env file
- Make sure you added billing at platform.openai.com
- Key should start with `sk-`

### "CORS error in browser"
- Make sure Flask is running on port 5000
- Make sure React is running on port 5173
- Check backend .env has correct settings

### "flask db migrate" fails
- Make sure PostgreSQL is running: `sudo service postgresql start`
- Check DATABASE_URL in .env matches your setup

---

## Deploying Online (for Resume Links)

### Free Deployment on Render.com

**Backend:**
1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect your repo → Select `backend/` folder
4. Build: `pip install -r requirements.txt`
5. Start: `gunicorn app:app`
6. Add Environment Variables (copy from .env)

**Frontend:**
1. Render → New Static Site
2. Build: `npm run build`
3. Publish dir: `dist`
4. Add env: `VITE_API_URL=https://your-backend.onrender.com`

**Database:**
- Render → New PostgreSQL (free tier available)
- Copy the connection string into DATABASE_URL

---

## GitHub Setup (for Portfolio)

```bash
cd ai-interview-prep
git init
git add .
git commit -m "Initial commit: AI Interview Prep Platform"

# Create repo on github.com, then:
git remote add origin https://github.com/YOURUSERNAME/ai-interview-prep.git
git branch -M main
git push -u origin main
```

**Make it look great on GitHub:**
- Add a screenshot of the dashboard to README
- Add topics: `python`, `nlp`, `machine-learning`, `react`, `flask`, `openai`
- Pin the repo on your profile

---

## Resume Description

Copy this into your resume:

> **AI-Powered Interview Preparation Platform** | Python, Flask, React, PostgreSQL, OpenAI GPT-4, spaCy, XGBoost
> Built an end-to-end interview prep system with NLP-based answer evaluation (sentence-transformers, spaCy NER), 
> LLM question generation (GPT-4/LangChain), XGBoost feedback scoring model, resume parsing, 
> and a React dashboard with analytics. Multi-user system with JWT auth, RESTful API, and company-specific prep (TCS, Amazon, Google).
