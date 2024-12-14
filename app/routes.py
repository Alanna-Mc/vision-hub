from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm
from app import app, db
from app.models import User, TrainingModule, UserModuleProgress, Option, UserQuestionAnswer
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


@app.route('/dashboard_training', methods=['GET'])
@login_required
def training_dashboard():
    if current_user.role.role_name != "staff":
        return redirect(url_for('logout'))
    
    # Fetch the onboarding steps and training modules for the user's path
    onboarding_path = current_user.onboarding_path
    if onboarding_path:
        steps = onboarding_path.steps
    else:
        steps = []
    
    return render_template('dashboard_training.html', title="Training Dashboard", steps=steps)


from datetime import datetime, timezone

@app.route('/staff/take_training_module/<int:module_id>', methods=['GET', 'POST'])
@login_required
def take_training_module(module_id):
    if current_user.role.role_name != 'staff':
        return redirect(url_for('logout'))
    
    module = TrainingModule.query.get_or_404(module_id)

    if request.method == 'POST':
        # User submitted their answers, save their progress.
        progress = UserModuleProgress(user_id=current_user.id, training_module_id=module_id, start_date=datetime.now(timezone.utc))
        db.session.add(progress)
        db.session.flush()

        # For each question, get the selected option
        for question in module.questions:
            selected_option_id = request.form.get(f'question_{question.id}')
            selected_option = Option.query.get(selected_option_id) if selected_option_id else None
            is_correct = selected_option.is_correct if selected_option else False

            answer = UserQuestionAnswer(
                progress=progress,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct
            )
            db.session.add(answer)

        # Calculate score
        score = sum(1 for ans in progress.answers if ans.is_correct)
        progress.score = score
        progress.completed_date = datetime.now(timezone.utc)

        db.session.commit()
        flash("Your training results have been saved!")
        return redirect(url_for('training_dashboard'))
    
    # If GET, show the module questions
    return render_template('take_training_module.html', module=module, title=module.module_title)
