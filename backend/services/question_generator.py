import os
import json
from groq import Groq

# NOTE: load_dotenv() should be called once in your main app (app.py), not here

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    return Groq(api_key=api_key)


COMPANY_STYLES = {
    "Amazon": "Focus on Leadership Principles (STAR format): Customer Obsession, Ownership, Invent & Simplify, Deliver Results.",
    "Google": "Focus on problem-solving, system design, and behavioral questions with data-driven answers.",
    "TCS": "Focus on technical fundamentals, communication skills, and HR questions about adaptability.",
    "Infosys": "Focus on technical aptitude, teamwork, process adherence, and scenario-based questions.",
    "Microsoft": "Focus on growth mindset, collaboration, technical depth, and real-world impact.",
    "General": "Mix of behavioral, technical, and situational questions appropriate for the role.",
}

QUESTION_TYPES = {
    "easy": "Ask straightforward HR and basic technical questions.",
    "medium": "Ask situational, behavioral (STAR), and intermediate technical questions.",
    "hard": "Ask deep technical, system design, and leadership/conflict-resolution questions.",
}


class QuestionGenerator:
    def generate(self, company: str, role: str, difficulty: str, resume_text: str = "", count: int = 5) -> list:
        client = get_client()  # ✅ FIX: properly initialize client

        company_style = COMPANY_STYLES.get(company, COMPANY_STYLES["General"])
        difficulty_guide = QUESTION_TYPES.get(difficulty, QUESTION_TYPES["medium"])

        resume_section = ""
        if resume_text:
            resume_section = f"\n\nCandidate's Resume Summary:\n{resume_text[:1500]}\nUse specific skills and experiences from this resume to personalize questions."

        prompt = f"""You are an expert interviewer at {company} hiring for a {role} position.

Company Style: {company_style}
Difficulty: {difficulty_guide}
{resume_section}

Generate exactly {count} interview questions. Return ONLY a JSON array with this structure:
[
  {{
    "question": "Question text here",
    "type": "behavioral|technical|hr|situational",
    "tip": "Brief tip on what a good answer covers (1 sentence)"
  }}
]

No preamble, no explanation. Just the JSON array."""

        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1200,
            )

            content = response.choices[0].message.content.strip()

            # Clean markdown if present
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:].strip()

            # Parse JSON safely
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                print("Invalid JSON from API")
                return self._fallback_questions(role, count)

        except Exception as e:
            print(f"Question generation error: {e}")
            return self._fallback_questions(role, count)

    def _fallback_questions(self, role: str, count: int) -> list:
        fallback = [
            {"question": f"Tell me about yourself and why you want this {role} position.", "type": "hr", "tip": "Be concise, highlight relevant skills."},
            {"question": "Describe a challenging project you worked on and how you handled it.", "type": "behavioral", "tip": "Use STAR format: Situation, Task, Action, Result."},
            {"question": "What are your greatest technical strengths?", "type": "technical", "tip": "Mention specific tools/technologies with examples."},
            {"question": "Where do you see yourself in 5 years?", "type": "hr", "tip": "Align your goals with company growth."},
            {"question": "Tell me about a time you had a conflict with a team member. How did you resolve it?", "type": "behavioral", "tip": "Focus on communication and positive outcome."},
        ]
        return fallback[:count]