from flask import  Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')        
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
  if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    role = request.form.get('role')
    user = User.query.filter_by(username=username).first()
    if user:
      flash('Username already exists', category='error')
    elif len(name)<2:
      flash('Name must be greater than 3 characters', category='error')
    elif len(email)<4:
      flash('Email must be greater than 3 characters', category='error')
    elif len(username)<4:
      flash('Username must be greater than 3 characters', category='error')
    elif password1 != password2:
      flash('Passwords do not match', category='error')
    elif role not in ['seeker', 'employer']: 
      flash('Invalid role selected.', category='error')
    else:
      new_user = User(name=name, email=email, username=username, password=generate_password_hash(password1), role=role)
      db.session.add(new_user)
      db.session.commit()
      flash('Account created', category='success')
      login_user(new_user, remember=True)
      return redirect(url_for('views.home'))

  return render_template("sign_up.html", user=current_user)
