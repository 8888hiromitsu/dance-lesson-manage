from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(50))
    selected_template = db.Column(db.String(50), default='template1')  # テンプレート選択を保存するフィールド

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    cancel_deadline = db.Column(db.DateTime)
    url = db.Column(db.String(200))

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_status = db.Column(db.String(50))

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'))
    amount = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(50))

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    satisfaction = db.Column(db.Integer)
    good_points = db.Column(db.Text)
    improvement_points = db.Column(db.Text)
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class AnalysisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_range = db.Column(db.String(100))
    update_count = db.Column(db.Integer, default=0)