import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from . import db
from .models import Job, Application, GeneralApplication

views = Blueprint('views', __name__)

UPLOAD_FOLDER = 'website/resume' 
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/', methods=['GET'])
@login_required
def home():
    jobs_query = Job.query.order_by(Job.posted_date.desc())
    search_term = request.args.get('search', '').strip()

    if search_term:
        jobs_query = jobs_query.filter(
            or_(
                Job.title.ilike(f'%{search_term}%'),
                Job.description.ilike(f'%{search_term}%'),
                Job.location.ilike(f'%{search_term}%')
            )
        )

    jobs = jobs_query.all()

    return render_template('home.html', user=current_user, jobs=jobs, search_term=search_term)

@views.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'employer':
        flash('You must be an employer to post a job.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills')
        location = request.form.get('location')

        if not all([title, description, required_skills, location]):
            flash('All fields are required.', 'error')
            return redirect(url_for('views.post_job'))

        new_job = Job(title=title,description=description,required_skills=required_skills,location=location,employer_id=current_user.id)
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('views.home'))

    return render_template('post_job.html', user=current_user)
@views.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)

    if current_user.role != 'seeker':
        flash('Only job seekers can apply for positions.', category='error')
        return redirect(url_for('views.home'))

    existing_application = Application.query.filter_by(job_id=job_id, seeker_id=current_user.id).first()
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('views.view_application', application_id=existing_application.id))

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No resume file part found', 'error')
            return redirect(request.url)

        file = request.files['resume']

        if file.filename == '' or not allowed_file(file.filename):
            flash('Invalid or missing file. Must be PDF or DOCX.', 'error')
            return redirect(request.url)

        filename = secure_filename(f'{current_user.id}_{job_id}_{file.filename}')
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        new_application = Application(job_id=job_id,seeker_id=current_user.id,resume_filename=filename,match_score=0.0,review_text="Application submitted. Review pending.")
        db.session.add(new_application)
        db.session.commit()

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('views.view_application', application_id=new_application.id))

    return render_template('apply_job.html', user=current_user, job=job)

@views.route('/application/<int:application_id>')
@login_required
def view_application(application_id):
    app_data = Application.query.get_or_404(application_id)

    if app_data.seeker_id != current_user.id and app_data.job.employer_id != current_user.id:
        flash('You do not have permission to view this application.', 'error')
        return redirect(url_for('views.home'))

    job = Job.query.get(app_data.job_id)
    return render_template('application_status.html', user=current_user, app_data=app_data, job=job)

@views.route('/general-apply', methods=['GET', 'POST'])
@login_required
def general_apply():
    if current_user.role != 'seeker':
        flash('You must be a job seeker to submit a general application.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No resume file part found', 'error')
            return redirect(request.url)

        file = request.files['resume']
        cover_letter = request.form.get('cover_letter')

        if file.filename == '' or not allowed_file(file.filename):
            flash('Invalid or missing file. Must be PDF or DOCX.', 'error')
            return redirect(request.url)

        filename = secure_filename(f'general_{current_user.id}_{file.filename}')
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(file_path)
        except Exception as e:
            flash(f'Error saving file: {e}', 'error')
            return redirect(request.url)

        new_application = GeneralApplication(seeker_id=current_user.id, resume_filename=filename,cover_letter=cover_letter)
        db.session.add(new_application)
        db.session.commit()

        flash('General application submitted successfully!', 'success')
        return redirect(url_for('views.home'))

    return render_template('general_apply.html', user=current_user)

@views.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(views.config['UPLOAD_FOLDER'], filename)

@views.route('/general-resume/<filename>')
@login_required
def download_general_resume(filename):
    if current_user.role != 'employer':
        flash('You must be an employer to view this file.', category='error')
        return redirect(url_for('views.home'))
    try:
        return send_from_directory(
            UPLOAD_FOLDER, 
            filename, 
            as_attachment=False
        )
    except FileNotFoundError:
        flash('Resume file not found.', 'error')
        return redirect(url_for('views.view_general_applications'))

@views.route('/view-general-applications')
@login_required
def view_general_applications():
    if current_user.role != 'employer':
        flash('You must be an employer to view general applications.', category='error')
        return redirect(url_for('views.home'))

    general_applications = GeneralApplication.query.all()

    return render_template('view_general_applications.html', user=current_user, applications=general_applications)