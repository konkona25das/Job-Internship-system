from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(150), unique=True)
  email = db.Column(db.String(150))
  password = db.Column(db.String(150))
  name = db.Column(db.String(150))
  role = db.Column(db.String(10), default='seeker')
  jobs_posted = db.relationship('Job', backref='employer', lazy=True)
  applications = db.relationship('Application', backref='applicant', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.String(500), nullable=False) 
    location = db.Column(db.String(50), nullable=False)
    posted_date = db.Column(db.DateTime(timezone=True), default=func.now())

    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False) 
    match_score = db.Column(db.Float, default=0.0)
    review_text = db.Column(db.Text, default="Review pending.")
    application_date = db.Column(db.DateTime(timezone=True), default=func.now())

class GeneralApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False) 
    cover_letter = db.Column(db.Text, default="No cover letter provided.")
    application_date = db.Column(db.DateTime(timezone=True), default=func.now())

    applicant = db.relationship('User', backref='general_applications', foreign_keys=[seeker_id])