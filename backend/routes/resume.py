from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.models import Resume
from services.resume_parser import ResumeParser

resume_bp = Blueprint("resume", __name__)
parser = ResumeParser()


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    parsed = parser.parse(file)

    resume = Resume(
        user_id=user_id,
        filename=file.filename,
        raw_text=parsed.get("raw_text", ""),
        skills=parsed.get("skills", []),
        experience_years=parsed.get("experience_years", 0),
        education=parsed.get("education", ""),
        extracted_roles=parsed.get("roles", []),
    )
    db.session.add(resume)
    db.session.commit()

    return jsonify({"resume": resume.to_dict(), "message": "Resume parsed successfully"}), 201


@resume_bp.route("/list", methods=["GET"])
@jwt_required()
def list_resumes():
    user_id = int(get_jwt_identity())
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).all()
    return jsonify({"resumes": [r.to_dict() for r in resumes]}), 200
