import sqlalchemy as sa
import os, secrets
from flask import render_template, flash, redirect, url_for, request, current_app
from app.forms import LoginForm
from app import app, db
from app.models import User, TrainingModule, UserModuleProgress, Option, UserQuestionAnswer
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from config import Config


@app.route('/login', methods=['GET', 'POST'])
def login():        
    if current_user.is_authenticated:
        if current_user.role.role_name == "admin":
            return redirect(url_for('admin_dashboard'))
        elif current_user.role.role_name == "manager":
            return redirect(url_for('manager_dashboard'))
        elif current_user.role.role_name == "staff":
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('logout'))
    
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


@app.route('/')
def index():
    return redirect(url_for('login'))


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

    onboarding_path = current_user.onboarding_path
    steps = onboarding_path.steps if onboarding_path else []
    active_modules = [step.training_module for step in steps if step.training_module.active]

    completed_modules = []
    to_be_completed_modules = []
    in_progress_modules = []

    passing_threshold = 0.5

    for module in active_modules:
        progress = UserModuleProgress.query.filter_by(
            user_id=current_user.id,
            training_module_id=module.id
        ).order_by(UserModuleProgress.id.desc()).first()

        # Status of current module
        if not progress:
            to_be_completed_modules.append(module)
        else:
            total_questions = len(module.questions) or 1  # Avoid division by zero
            if progress.completed_date:
                # Passed
                if progress.score is not None and (progress.score / total_questions) >= passing_threshold:
                    completed_modules.append({
                        'module': module,        
                        'score': progress.score, 
                        'passed': True           
                    })
                # Failed                    
                else:
                    to_be_completed_modules.append(module)
            # Incomplete attempt (in progress)
            else:
                in_progress_modules.append(module)

    return render_template(
        'dashboard_training.html', 
        title="Training Dashboard", 
        to_be_completed_modules=to_be_completed_modules, 
        in_progress_modules=in_progress_modules, 
        completed_modules=completed_modules
    )


@app.route('/staff/take_training_module/<int:module_id>', methods=['GET', 'POST'])
@login_required
def take_training_module(module_id):
    if current_user.role.role_name != 'staff':
        return redirect(url_for('logout'))
    
    module = TrainingModule.query.get_or_404(module_id)

    passing_threshold = 0.5

    # Get latest attempt for current module
    progress = UserModuleProgress.query.filter_by(
        user_id=current_user.id,
        training_module_id=module_id
    ).order_by(UserModuleProgress.id.desc()).first()

    # Create a new attept if needed
    if request.method == 'GET':
        # Module has progress
        if progress:
            total_questions = len(module.questions) or 1
            # Module completed
            if progress.completed_date:
                # Was it passed?
                if progress.score is not None and (progress.score / total_questions) < passing_threshold:
                    # Failed attempt
                    progress = UserModuleProgress(
                        user_id=current_user.id,
                        training_module_id=module_id,
                        start_date=datetime.now(timezone.utc)
                    )
                    db.session.add(progress)
                    db.session.commit()
        # No progress 
        else:
            progress = UserModuleProgress(
                user_id=current_user.id,
                training_module_id=module_id,
                start_date=datetime.now(timezone.utc)
            )
            db.session.add(progress)
            db.session.commit()

    # On submit
    if request.method == 'POST':
        action = request.form.get('action', 'submit')
        
        # Create progress for the user if they do not have any
        if not progress:
            progress = UserModuleProgress(
                user_id=current_user.id, 
                training_module_id=module_id, 
                start_date=datetime.now(timezone.utc)
            )
            db.session.add(progress)
            db.session.flush()

        existing_answers = {ans.question_id: ans for ans in progress.answers}

        for question in module.questions:
            selected_option_id = request.form.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = Option.query.get(selected_option_id)
                is_correct = selected_option.is_correct if selected_option else False

                # Update existing answer
                if question.id in existing_answers:
                    existing_answers[question.id].selected_option = selected_option
                    existing_answers[question.id].is_correct = is_correct
                # Add new answer
                else:
                    new_answer = UserQuestionAnswer(
                        progress=progress, question=question, selected_option=selected_option, 
                        is_correct=is_correct
                    )
                    db.session.add(new_answer)

        # Save users current progress
        if action == "save":
            db.session.commit()
            flash("Your progress has been saved")
            return redirect(url_for('training_dashboard'))
        # Submit answers
        else:
            correct_answers = sum(1 for ans in progress.answers if ans.is_correct)
            total_questions = len(module.questions)
            progress.score = correct_answers
            progress.completed_date = datetime.now(timezone.utc)

            if (correct_answers / total_questions) >= passing_threshold:
                flash("Module completed! You passed.")
            else:
                flash("Module completed, but you did not pass. Please retake module.")
            
            db.session.commit() 
            return redirect(url_for('training_dashboard'))

    # Load saved progress if any
    user_answers = {}
    if progress and not progress.completed_date:
        for ans in progress.answers:
            user_answers[ans.question_id] = ans.selected_option_id

    return render_template('take_training_module.html', 
                           module=module, 
                           title=module.module_title, 
                           user_answers=user_answers)


@app.route('/update_profile_photo', methods=['POST'])
@login_required
def update_profile_photo():
    photo = request.files.get('photo')
    if not photo or photo.filename == '':
        return redirect(request.form.get('next'))

    if not current_app.config['ALLOWED_EXTENSIONS'] or \
       not Config.allowed_file(photo.filename):
        return redirect(request.form.get('next'))

    rand = secrets.token_hex(8)
    _, ext = os.path.splitext(secure_filename(photo.filename))
    filename = rand + ext.lower()

    old = current_user.profile_photo or ''
    if old != 'profileDefault.png':
        old_path = os.path.join(current_app.config['PROFILE_PHOTO_FOLDER'], old)
        if os.path.exists(old_path):
            os.remove(old_path)

    save_path = os.path.join(current_app.config['PROFILE_PHOTO_FOLDER'], filename)
    photo.save(save_path)

    current_user.profile_photo = filename
    db.session.commit()

    return redirect(request.form.get('next'))