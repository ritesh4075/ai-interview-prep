import os
from dotenv import load_dotenv

load_dotenv()  # ok for now, but better in app.py

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/interview_prep_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.urandom(24)
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    # ✅ Updated to Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "interview-prep-resumes")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB