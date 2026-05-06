from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:5173"])

    from routes.auth import auth_bp
    from routes.interview import interview_bp
    from routes.resume import resume_bp
    from routes.feedback import feedback_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(interview_bp, url_prefix="/api/interview")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "AI Interview Prep API running"}

    return app
    

app = create_app()
@app.route("/")
def home():
    return "API is running 🚀"

if __name__ == "__main__":
    app.run(debug=True)
