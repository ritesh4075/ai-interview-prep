import re
import spacy
import pdfplumber

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "flask", "django", "fastapi", "spring", "sql", "postgresql",
    "mysql", "mongodb", "redis", "aws", "gcp", "azure", "docker", "kubernetes",
    "git", "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau",
    "power bi", "excel", "r", "matlab", "spark", "hadoop", "kafka", "airflow",
    "data analysis", "data visualization", "statistics", "regression", "classification",
    "clustering", "neural network", "transformer", "bert", "gpt", "llm",
    "c++", "c#", "go", "rust", "kotlin", "swift", "html", "css", "graphql",
    "rest api", "microservices", "agile", "scrum", "ci/cd", "linux", "bash",
]

EDUCATION_KEYWORDS = ["b.tech", "b.e", "m.tech", "m.e", "mca", "bca", "bsc", "msc",
                       "bachelor", "master", "phd", "diploma", "engineering", "computer science",
                       "information technology", "data science", "iit", "nit", "bits"]

ROLE_KEYWORDS = ["engineer", "developer", "analyst", "scientist", "architect", "manager",
                  "intern", "associate", "lead", "senior", "junior", "consultant", "specialist"]


class ResumeParser:

    def parse(self, file_obj) -> dict:
        raw_text = self._extract_text(file_obj)
        if not raw_text:
            return {"raw_text": "", "skills": [], "experience_years": 0, "education": "", "roles": []}

        skills = self._extract_skills(raw_text)
        experience_years = self._extract_experience(raw_text)
        education = self._extract_education(raw_text)
        roles = self._extract_roles(raw_text)

        return {
            "raw_text": raw_text,
            "skills": skills,
            "experience_years": experience_years,
            "education": education,
            "roles": roles,
        }

    def _extract_text(self, file_obj) -> str:
        try:
            text_parts = []
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""

    def _extract_skills(self, text: str) -> list:
        text_lower = text.lower()
        found_skills = []
        for skill in SKILL_KEYWORDS:
            if skill in text_lower:
                found_skills.append(skill.title() if len(skill) > 4 else skill.upper())
        return list(dict.fromkeys(found_skills))  # preserve order, remove duplicates

    def _extract_experience(self, text: str) -> float:
        patterns = [
            r"(\d+)\+?\s*years?\s+of\s+experience",
            r"(\d+)\+?\s*years?\s+experience",
            r"experience\s*[:\-]?\s*(\d+)\+?\s*years?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1))

        # Estimate from date ranges
        year_matches = re.findall(r"\b(20\d{2}|19\d{2})\b", text)
        if len(year_matches) >= 2:
            years = sorted([int(y) for y in year_matches])
            span = years[-1] - years[0]
            if 0 < span < 40:
                return float(span)
        return 0.0

    def _extract_education(self, text: str) -> str:
        text_lower = text.lower()
        lines = text.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(edu in line_lower for edu in EDUCATION_KEYWORDS):
                cleaned = line.strip()
                if 5 < len(cleaned) < 200:
                    return cleaned
        return ""

    def _extract_roles(self, text: str) -> list:
        nlp = get_nlp()
        doc = nlp(text[:3000])
        roles = []

        lines = text.split("\n")
        for line in lines:
            line_lower = line.lower().strip()
            if any(role in line_lower for role in ROLE_KEYWORDS) and len(line_lower) < 80:
                cleaned = line.strip()
                if cleaned and cleaned not in roles:
                    roles.append(cleaned)

        return roles[:5]
