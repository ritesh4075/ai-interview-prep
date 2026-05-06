"""
Seed script — creates a test user and sample data.
Run: python scripts/seed_db.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from models.models import User

app = create_app()

with app.app_context():
    db.create_all()

    # Create test user if doesn't exist
    if not User.query.filter_by(email='test@example.com').first():
        user = User(name='Test User', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print('✅ Test user created: test@example.com / password123')
    else:
        print('ℹ️  Test user already exists')

    print('✅ Database seeded successfully')
