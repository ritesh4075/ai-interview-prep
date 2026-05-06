from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.models import Response, Feedback, Interview
from services.answer_evaluator import AnswerEvaluator
from services.feedback_scorer import FeedbackScorer

feedback_bp = Blueprint("feedback", __name__)
evaluator = AnswerEvaluator()
scorer = FeedbackScorer()


@feedback_bp.route("/evaluate/<int:response_id>", methods=["POST"])
@jwt_required()
def evaluate_response(response_id):
    user_id = int(get_jwt_identity())
    response = Response.query.get(response_id)

    if not response:
        return jsonify({"error": "Response not found"}), 404

    interview = Interview.query.filter_by(id=response.interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({"error": "Unauthorized"}), 403

    if response.feedback:
        return jsonify({"feedback": response.feedback.to_dict()}), 200

    evaluation = evaluator.evaluate(
        question=response.question,
        answer=response.answer_text,
        company=interview.company,
        role=interview.role,
    )

    overall = scorer.score(evaluation)

    feedback = Feedback(
        response_id=response_id,
        keyword_score=evaluation["keyword_score"],
        clarity_score=evaluation["clarity_score"],
        semantic_score=evaluation["semantic_score"],
        confidence_score=evaluation.get("confidence_score", 0.5),
        overall_score=overall,
        suggestions=evaluation["suggestions"],
        ideal_answer=evaluation["ideal_answer"],
        keywords_found=evaluation["keywords_found"],
        keywords_missing=evaluation["keywords_missing"],
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({"feedback": feedback.to_dict()}), 201


@feedback_bp.route("/summary/<int:interview_id>", methods=["GET"])
@jwt_required()
def get_summary(interview_id):
    user_id = int(get_jwt_identity())
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    responses = [r.to_dict() for r in interview.responses]
    scores = [r["feedback"]["overall_score"] for r in responses if r["feedback"]]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    return jsonify({
        "interview": interview.to_dict(),
        "responses": responses,
        "avg_score": avg_score,
        "total_questions": len(responses),
        "evaluated": len(scores),
    }), 200
