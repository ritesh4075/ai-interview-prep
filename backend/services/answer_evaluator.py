import os
import textstat
import spacy
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Lazy-loaded globals
_nlp = None
_embedder = None
_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set")
        _client = Groq(api_key=api_key)
    return _client


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


FILLER_WORDS = {
    "um", "uh", "like", "you know", "basically",
    "literally", "actually", "so yeah", "i mean"
}

DOMAIN_KEYWORDS = {
    "behavioral": ["team", "challenge", "result", "action", "situation", "task", "learned", "delivered"],
    "technical": ["algorithm", "database", "api", "deploy", "optimize", "debug", "architecture"],
    "hr": ["growth", "skills", "career", "motivation", "opportunity", "culture"],
    "situational": ["would", "handle", "approach", "resolve", "prioritize"],
}


class AnswerEvaluator:

    def evaluate(self, question: str, answer: str, company: str = "General", role: str = "") -> dict:
        if not answer or len(answer.strip()) < 10:
            return self._empty_feedback()

        ideal_answer = self._get_ideal_answer(question, role, company)

        keyword_score, keywords_found, keywords_missing = self._keyword_score(answer, question)
        clarity_score = self._clarity_score(answer)
        semantic_score = self._semantic_similarity(answer, ideal_answer)
        confidence_score = self._confidence_score(answer)
        star_score = self._calculate_star_score(answer)

        suggestions = self._generate_suggestions(
            answer, keyword_score, clarity_score, semantic_score, keywords_missing
        )

        return {
            "keyword_score": keyword_score,
            "clarity_score": clarity_score,
            "semantic_score": semantic_score,
            "confidence_score": confidence_score,
            "star_score": star_score,
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "suggestions": suggestions,
            "ideal_answer": ideal_answer,
        }

    # STAR scoring
    def _calculate_star_score(self, answer: str) -> float:
        ans = answer.lower()

        score = 0
        if "situation" in ans:
            score += 2
        if "task" in ans:
            score += 2
        if "action" in ans:
            score += 3
        if "result" in ans:
            score += 3

        return min(score, 10) / 10

    def _get_ideal_answer(self, question: str, role: str, company: str) -> str:
        try:
            client = get_client()

            prompt = f"""
For this interview question at {company} for {role} role:
"{question}"

Give a concise 3-4 sentence ideal answer.
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print("Groq error:", e)
            return ""

    def _keyword_score(self, answer: str, question: str):
        nlp = get_nlp()

        answer_lower = answer.lower()
        q_type = self._detect_question_type(question)

        domain_kws = DOMAIN_KEYWORDS.get(q_type, DOMAIN_KEYWORDS["behavioral"])
        found = [kw for kw in domain_kws if kw in answer_lower]
        missing = [kw for kw in domain_kws if kw not in answer_lower]

        score = len(found) / max(len(domain_kws), 1)

        return min(score, 1.0), found, missing[:5]

    def _clarity_score(self, answer: str) -> float:
        try:
            fk = textstat.flesch_reading_ease(answer)
            return round(min(max(fk / 80, 0), 1), 2)
        except:
            return 0.5

    def _semantic_similarity(self, answer: str, ideal: str) -> float:
        if not answer or not ideal:
            return 0.5
        try:
            embedder = get_embedder()
            vecs = embedder.encode([answer, ideal])
            sim = cosine_similarity([vecs[0]], [vecs[1]])[0][0]
            return round(float(sim) * 100, 2)
        except:
            return 0.5

    def _confidence_score(self, answer: str) -> float:
        words = answer.lower().split()
        filler = sum(1 for w in words if w in FILLER_WORDS)
        ratio = filler / max(len(words), 1)
        return round(1 - min(ratio * 5, 1), 2)

    def _generate_suggestions(self, answer, keyword_score, clarity_score, semantic_score, missing_kws):
        suggestions = []

        if len(answer.split()) < 50:
            suggestions.append("Expand answer to 100-200 words with examples.")

        if keyword_score < 0.4:
            suggestions.append(f"Add keywords: {', '.join(missing_kws[:3])}")

        if clarity_score < 0.4:
            suggestions.append("Use simpler sentences.")

        if semantic_score < 40:
            suggestions.append("Answer doesn't fully address the question.")

        if "situation" not in answer.lower() or "result" not in answer.lower():
            suggestions.append("Use STAR format.")

        return " | ".join(suggestions)

    def _detect_question_type(self, question: str) -> str:
        q = question.lower()

        if "tell me about a time" in q:
            return "behavioral"
        if "how would you" in q:
            return "situational"
        if any(x in q for x in ["algorithm", "database", "system"]):
            return "technical"

        return "hr"

    def _empty_feedback(self):
        return {
            "keyword_score": 0,
            "clarity_score": 0,
            "semantic_score": 0,
            "confidence_score": 0,
            "star_score": 0,
            "keywords_found": [],
            "keywords_missing": [],
            "suggestions": "No answer provided",
            "ideal_answer": "",
        }