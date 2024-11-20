from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm
from app import app, db
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa


@app.route('/index')
#  Decorator part of Flask-login that prevents unautherised access by requiring login
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():        
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        
        # Check if user exists and password matches
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        # Log the user in
        login_user(user, remember=form.remember_me.data)

        # Get next_page if the user was trying to access a specific page
        next_page = request.args.get('next')
        if next_page and urlsplit(next_page).netloc == '':
            return redirect(next_page)
        
        # Redirect user based on role
        if user.role.role_name == "Admin":
            return redirect(url_for('admin_dashboard'))
        #elif user.role.role_name == "Manager":
         #   return redirect(url_for('manager_dashboard'))
        #elif user.role.role_name == "Staff":
         #   return redirect(url_for('staff_dashboard'))
        else:
            # Temp redirect for non-admins
            return redirect(url_for('index'))
    
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
