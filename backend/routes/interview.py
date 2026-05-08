from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from models.models import Interview, Response, Resume
from services.question_generator import QuestionGenerator
from services.voice_analyzer import VoiceAnalyzer

interview_bp = Blueprint("interview", __name__)

question_gen = QuestionGenerator()
voice_analyzer = VoiceAnalyzer()

# =========================
# 🎤 SPEECH TO TEXT ROUTE
# =========================
@interview_bp.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    audio = request.files["audio"]

    result = voice_analyzer.analyze(audio)

    return jsonify({
        "text": result["transcript"]
    })


# =========================
# START INTERVIEW
# =========================
@interview_bp.route("/start", methods=["POST"])
@jwt_required()
def start_interview():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    company = data.get("company", "General")
    role = data.get("role", "Software Engineer")
    difficulty = data.get("difficulty", "medium")
    resume_id = data.get("resume_id")

    interview = Interview(
        user_id=user_id,
        company=company,
        role=role,
        difficulty=difficulty,
        resume_id=resume_id,
    )

    db.session.add(interview)
    db.session.commit()

    resume_text = ""

    if resume_id:
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if resume:
            resume_text = resume.raw_text or ""

    questions = question_gen.generate(
        company=company,
        role=role,
        difficulty=difficulty,
        resume_text=resume_text,
        count=5,
    )

    return jsonify({
        "interview": interview.to_dict(),
        "questions": questions,
    }), 201


# =========================
# SUBMIT ANSWER
# =========================
@interview_bp.route("/<int:interview_id>/answer", methods=["POST"])
@jwt_required()
def submit_answer(interview_id):
    user_id = int(get_jwt_identity())

    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=user_id
    ).first()

    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    data = request.get_json()

    response = Response(
        interview_id=interview_id,
        question=data.get("question", ""),
        question_type=data.get("question_type", "behavioral"),
        answer_text=data.get("answer_text", ""),
    )

    db.session.add(response)
    db.session.commit()

    return jsonify({
        "response_id": response.id,
        "message": "Answer submitted"
    }), 201


# =========================
# END INTERVIEW
# =========================
@interview_bp.route("/<int:interview_id>/end", methods=["POST"])
@jwt_required()
def end_interview(interview_id):
    user_id = int(get_jwt_identity())

    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=user_id
    ).first()

    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    feedbacks = [r.feedback for r in interview.responses if r.feedback]

    if feedbacks:
        avg = sum(f.overall_score for f in feedbacks) / len(feedbacks)
        interview.overall_score = round(avg, 1)

    interview.status = "completed"
    interview.ended_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"interview": interview.to_dict()}), 200


# =========================
# HISTORY
# =========================
@interview_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())

    interviews = (
        Interview.query.filter_by(user_id=user_id)
        .order_by(Interview.started_at.desc())
        .limit(20)
        .all()
    )

    return jsonify({
        "interviews": [i.to_dict() for i in interviews]
    }), 200