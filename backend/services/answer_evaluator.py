import os
import re
import json
import textstat
import numpy as np
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

def _star_score(self, answer: str) -> float:
    ans = answer.lower()

    score = 0
    if "situation" in ans: score += 1
    if "task" in ans: score += 1
    if "action" in ans: score += 1
    if "result" in ans: score += 1

    return score / 4


FILLER_WORDS = {"um", "uh", "like", "you know", "basically", "literally", "actually", "so yeah", "i mean"}

DOMAIN_KEYWORDS = {
    "behavioral": ["team", "challenge", "result", "action", "situation", "task", "learned", "improved", "delivered", "led"],
    "technical": ["algorithm", "complexity", "database", "api", "deploy", "optimize", "debug", "architecture", "model", "pipeline"],
    "hr": ["growth", "motivated", "contribute", "career", "skills", "opportunity", "passion", "goal", "culture"],
    "situational": ["would", "prioritize", "approach", "handle", "resolve", "communicate", "ensure", "strategy"],
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
        star_score = self._star_score(answer)

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

    def _get_ideal_answer(self, question: str, role: str, company: str) -> str:
        try:
            client = get_client()

            prompt = f"""For this interview question at {company} for {role} role:
"{question}"

Provide a concise ideal answer in 3-4 sentences that covers the key points. Be specific."""

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Groq error: {e}")
            return ""

    def _keyword_score(self, answer: str, question: str) -> tuple:
        nlp = get_nlp()
        answer_lower = answer.lower()
        question_lower = question.lower()

        q_doc = nlp(question_lower)
        important_words = [
            token.lemma_ for token in q_doc
            if not token.is_stop and not token.is_punct and len(token.text) > 3
        ]

        q_type = self._detect_question_type(question)
        domain_kws = DOMAIN_KEYWORDS.get(q_type, DOMAIN_KEYWORDS["behavioral"])
        all_expected = list(set(domain_kws[:5]))
        found = [kw for kw in all_expected if kw in answer_lower]
        missing = [kw for kw in domain_kws if kw not in answer_lower][:5]

        score = len(found) / max(len(all_expected), 1)
        return min(score, 1.0), found[:8], missing[:5]

    def _clarity_score(self, answer: str) -> float:
        if len(answer.split()) < 5:
            return 0.1
        try:
            fk_score = textstat.flesch_reading_ease(answer)
            normalized = min(max(fk_score / 80, 0), 1)
            return round(normalized, 2)
        except Exception:
            return 0.5

    def _semantic_similarity(self, answer: str, ideal: str) -> float:
        if not ideal or not answer:
            return 0.5
        try:
            embedder = get_embedder()
            vecs = embedder.encode([answer, ideal])
            sim = cosine_similarity([vecs[0]], [vecs[1]])[0][0]
            return round(float(sim) * 100, 2)
        except Exception:
            return 0.5

    def _confidence_score(self, answer: str) -> float:
        words = answer.lower().split()
        filler_count = sum(1 for w in words if w in FILLER_WORDS)
        word_count = max(len(words), 1)
        filler_ratio = filler_count / word_count
        confidence = 1.0 - min(filler_ratio * 5, 1.0)
        return round(confidence, 2)

    def _generate_suggestions(self, answer, keyword_score, clarity_score, semantic_score, missing_kws):
        suggestions = []
        
        if len(answer.split()) < 50:
            suggestions.append("Your answer is too brief. Aim for 100-200 words with specific examples.")
        if keyword_score < 0.4:
            suggestions.append(f"Include more relevant keywords. Missing: {', '.join(missing_kws[:3])}.")
        if clarity_score < 0.4:
            suggestions.append("Simplify your language. Use shorter sentences for clarity.")
        if semantic_score < 40:
            suggestions.append("Your answer doesn't fully address the question.")
        if "situation" not in answer.lower() or "result" not in answer.lower():
            suggestions.append("Use STAR method (Situation, Action, Result) for better structure.")
        if not suggestions:
            suggestions.append("Good answer! Add a quantifiable result to strengthen it.")
        
        return " | ".join(suggestions)

    def _detect_question_type(self, question: str) -> str:
        q_lower = question.lower()
        if any(w in q_lower for w in ["tell me about a time", "describe a situation", "give an example"]):
            return "behavioral"
        if any(w in q_lower for w in ["how would you", "what would you do", "if you were"]):
            return "situational"
        if any(w in q_lower for w in ["algorithm", "code", "design", "system", "database", "complexity"]):
            return "technical"
        return "hr"

    def _empty_feedback(self) -> dict:
        return {
            "keyword_score": 0.0,
            "clarity_score": 0.0,
            "semantic_score": 0.0,
            "confidence_score": 0.0,
            "keywords_found": [],
            "keywords_missing": [],
            "suggestions": "Please provide an answer to evaluate.",
            "ideal_answer": "",
        }
    