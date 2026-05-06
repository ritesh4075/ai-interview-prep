from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    subscription_tier = db.Column(db.String(20), default="free")  # free | pro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship("Resume", backref="user", lazy=True)
    interviews = db.relationship("Interview", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat(),
        }


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(256))
    s3_url = db.Column(db.String(512))
    raw_text = db.Column(db.Text)
    skills = db.Column(db.ARRAY(db.String))
    experience_years = db.Column(db.Float, default=0)
    education = db.Column(db.String(256))
    extracted_roles = db.Column(db.ARRAY(db.String))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "skills": self.skills or [],
            "experience_years": self.experience_years,
            "education": self.education,
            "extracted_roles": self.extracted_roles or [],
            "uploaded_at": self.uploaded_at.isoformat(),
        }


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    company = db.Column(db.String(100), default="General")
    role = db.Column(db.String(100), default="Software Engineer")
    difficulty = db.Column(db.String(20), default="medium")  # easy | medium | hard
    status = db.Column(db.String(20), default="active")      # active | completed
    overall_score = db.Column(db.Float, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    responses = db.relationship("Response", backref="interview", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "difficulty": self.difficulty,
            "status": self.status,
            "overall_score": self.overall_score,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }


class Response(db.Model):
    __tablename__ = "responses"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default="behavioral")
    answer_text = db.Column(db.Text)
    audio_url = db.Column(db.String(512), nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    feedback = db.relationship("Feedback", backref="response", uselist=False, lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "question_type": self.question_type,
            "answer_text": self.answer_text,
            "answered_at": self.answered_at.isoformat(),
            "feedback": self.feedback.to_dict() if self.feedback else None,
        }


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey("responses.id"), unique=True, nullable=False)
    keyword_score = db.Column(db.Float, default=0.0)   # 0-1
    clarity_score = db.Column(db.Float, default=0.0)   # 0-1
    semantic_score = db.Column(db.Float, default=0.0)  # 0-1
    confidence_score = db.Column(db.Float, default=0.0)# 0-1
    overall_score = db.Column(db.Float, default=0.0)   # 0-10
    suggestions = db.Column(db.Text)
    ideal_answer = db.Column(db.Text)
    keywords_found = db.Column(db.ARRAY(db.String))
    keywords_missing = db.Column(db.ARRAY(db.String))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "keyword_score": round(self.keyword_score, 2),
            "clarity_score": round(self.clarity_score, 2),
            "semantic_score": round(self.semantic_score, 2),
            "confidence_score": round(self.confidence_score, 2),
            "overall_score": round(self.overall_score, 1),
            "suggestions": self.suggestions,
            "ideal_answer": self.ideal_answer,
            "keywords_found": self.keywords_found or [],
            "keywords_missing": self.keywords_missing or [],
        }
