from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm
from app import app, db
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():        
    if current_user.is_authenticated:
        # Redirect authenticated users to their correct dashboards
        if current_user.role.role_name == "admin":
            return redirect(url_for('admin_dashboard'))
        elif current_user.role.role_name == "manager":
            return redirect(url_for('manager_dashboard'))
        elif current_user.role.role_name == "staff":
            return redirect(url_for('staff_dashboard'))
        else:
            # Handle unauthenticated roles
            return redirect(url_for('logout'))
    
    # Login form logic
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
        if user.role.role_name == "admin":
            return redirect(url_for('admin_dashboard'))            
        elif user.role.role_name == "manager":
            return redirect(url_for('manager_dashboard'))
        elif user.role.role_name == "staff":
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('logout'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard_staff')
@login_required
def staff_dashboard():
    if current_user.role.role_name!= "staff":
        return redirect(url_for('login'))
    return render_template('/dashboard_staff.html', title='Staff Dashboard')


@app.route('/dashboard_manager')
@login_required
def manager_dashboard():
    if current_user.role.role_name!= "manager":
        return redirect(url_for('login'))
    return render_template('/dashboard_manager.html', title='Manger Dashboard')