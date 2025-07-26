# Login functionality was developed with the support of Miguel Grinberg's The 
# Flash Mega Tutorial series

import os
import secrets
from datetime import datetime, timezone
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import (
    render_template, 
    flash, redirect, 
    url_for, 
    request, 
    current_app
)
from flask_login import (
    current_user, 
    login_user, 
    logout_user, 
    login_required
)
from werkzeug.utils import secure_filename

from app.forms import LoginForm
from app import app, db
from app.models import (
    User, 
    TrainingModule, 
    UserModuleProgress, 
    Option, 
    UserQuestionAnswer
)
from config import Config

"""Routes for user authentication and dashboard management

This file handles user login/logout, dashboard rendering for staff and 
manager roles, staff training workflows, and profile photo upload.
"""
@app.route('/login', methods=['GET', 'POST'])
def login():      
    """Authenticate a user and redirect to role-specific dashboard.

    Displays the login form and processes credentials on POST. On successful
    authentication, redirects users based on their role. Rejects invalid
    credentials with a flash message.

    Returns:
        Response:
            - Rendered login template on GET or invalid credentials.
            - Redirect to admin, manager, or staff dashboard on successful login.
    """
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
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if next_page and urlsplit(next_page).netloc == '':                
            return redirect(next_page)
        
        if user.role.role_name == "admin":
            return redirect(url_for('admin_dashboard'))            
        elif user.role.role_name == "manager":
            return redirect(url_for('manager_dashboard'))
        elif user.role.role_name == "staff":
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('logout'))

    return render_template(
        'login.html', 
        title='Sign In', 
        form=form
    )


@app.route('/')
def index():
    """Redirect to the login page."""
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Logs out the current user and redirects to the login page."""
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard_staff')
@login_required
def staff_dashboard():
    """Render the staff dashboard if user is staff."""
    if current_user.role.role_name != "staff":
        return redirect(url_for('login'))
   
    return render_template(
        '/dashboard_staff.html',
        title='Staff Dashboard'
    )


@app.route('/dashboard_manager')
@login_required
def manager_dashboard():
    """Render the manager dashboard if user is a manager."""
    if current_user.role.role_name != "manager":
        return redirect(url_for('login'))
    
    return render_template(
        '/dashboard_manager.html', 
        title='Manager Dashboard'
    )


@app.route('/dashboard_training', methods = ['GET'])
@login_required
def training_dashboard():
    """Display training modules for staff users.

    Renders a dashboard showing training modules that are either completed,
    in progress, or yet to be started by the staff user.

    Returns:
        - Redirect to logout if the current user isn't staff.
        - Rendered “dashboard_training.html” with three lists:
        `to_be_completed_modules`, `in_progress_modules`, and `completed_modules`.
    """
    if current_user.role.role_name != "staff":
        return redirect(url_for('logout'))

    onboarding_path = current_user.onboarding_path
    steps = onboarding_path.steps if onboarding_path else []
    active_modules = [
        step.training_module for step in steps if step.training_module.active
    ]

    completed_modules = []
    to_be_completed_modules = []
    in_progress_modules = []
    passing_threshold = 0.5

    for module in active_modules:
        progress = UserModuleProgress.query.filter_by(
            user_id=current_user.id,
            training_module_id=module.id
        ).order_by(UserModuleProgress.id.desc()).first()

        if not progress:
            to_be_completed_modules.append(module)
        else:
            total_questions = len(module.questions) or 1 
            if progress.completed_date:
                if (progress.score is not None
                        and (progress.score / total_questions) >= passing_threshold):
                    completed_modules.append({
                        'module': module,
                        'score': progress.score,
                        'passed': True
                    })
                else:
                    to_be_completed_modules.append(module)
            else:
                in_progress_modules.append(module)

    return render_template(
        'dashboard_training.html', 
        title="Training Dashboard", 
        to_be_completed_modules=to_be_completed_modules, 
        in_progress_modules=in_progress_modules, 
        completed_modules=completed_modules
    )


@app.route('/staff/take_training_module/<int:module_id>', methods = ['GET', 'POST'])
@login_required
def take_training_module(module_id):
    """Handles the staff users training module session.

    On GET:
      - Retrieves or creates a UserModuleProgress record for the given module.
      - If the last attempt was failed, starts a fresh attempt.
      - Leaves in-progress attempts intact for continuation.

    On POST:
      - Records each submitted answer, updating existing answers or creating new ones.
      - If `action == "save"`, commits progress without completing the module.
      - Otherwise, computes the final score, marks completion, flashes a pass/fail message,
        and commits.

    Args:
        module_id (int): The ID of the training module to be taken.
   
    Returns:
        Response:
            - Redirects to logout if the user is not in staff role.
            - Renders 'take_training_module.html' with the module and any of the
            users previous answers.
            - Redirects to the training dashboard after saving or submitting 
            answers.
    """
    if current_user.role.role_name != 'staff':
        return redirect(url_for('logout'))
    
    module = TrainingModule.query.get_or_404(module_id)
    passing_threshold = 0.5

    progress = UserModuleProgress.query.filter_by(
        user_id=current_user.id,
        training_module_id=module_id
    ).order_by(UserModuleProgress.id.desc()).first()

    if request.method == 'GET':
        if progress:
            total_questions = len(module.questions) or 1
            if progress.completed_date:
                if (progress.score is not None
                        and (progress.score / total_questions) < passing_threshold):
                    progress = UserModuleProgress(
                        user_id=current_user.id,
                        training_module_id=module_id,
                        start_date=datetime.now(timezone.utc)
                    )
                    db.session.add(progress)
                    db.session.commit()
        else:
            progress = UserModuleProgress(
                user_id=current_user.id,
                training_module_id=module_id,
                start_date=datetime.now(timezone.utc)
            )
            db.session.add(progress)
            db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action', 'submit')
        
        if not progress:
            progress = UserModuleProgress(
                user_id = current_user.id,
                training_module_id = module_id,
                start_date = datetime.now(timezone.utc)
            )
            db.session.add(progress)
            db.session.flush()

        existing_answers = {ans.question_id: ans for ans in progress.answers}

        for question in module.questions:
            selected_option_id = request.form.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = Option.query.get(selected_option_id)
                is_correct = selected_option.is_correct if selected_option else False

                if question.id in existing_answers:
                    existing_answers[question.id].selected_option = selected_option
                    existing_answers[question.id].is_correct = is_correct
                else:
                    new_answer = UserQuestionAnswer(
                        progress = progress, 
                        question = question, 
                        selected_option = selected_option, 
                        is_correct = is_correct
                    )
                    db.session.add(new_answer)

        if action == "save":
            db.session.commit()
            flash("Your progress has been saved")
            return redirect(url_for('training_dashboard'))
        else:
            correct_answers = sum(1 for ans in progress.answers if ans.is_correct)
            total_questions = len(module.questions)
            progress.score = correct_answers
            progress.completed_date = datetime.now(timezone.utc)

            if (correct_answers / total_questions) >= passing_threshold:
                flash("Module completed! You passed.")
            else:
                flash("Module failed, please retake module.")
            
            db.session.commit() 
            return redirect(url_for('training_dashboard'))

    user_answers = {}
    if progress and not progress.completed_date:
        for ans in progress.answers:
            user_answers[ans.question_id] = ans.selected_option_id

    return render_template(
        'take_training_module.html',
        module=module,
        title=module.module_title,
        user_answers=user_answers
    )


@app.route('/update_profile_photo', methods = ['POST'])
@login_required
def update_profile_photo():
    """Upload and set a new profile photo for the current user.

    Validates and saves an uploaded image file, replacing any existing custom
    profile photo. 

    Details:
        - Rejects requests with no file or an empty filename.
        - Ensures the uploaded file has an allowed extension.
        - Generates a random filename.
        - Removes previously uploaded photo file.
        - Saves the new file under `PROFILE_PHOTO_FOLDER` and updates the user 
        record.

    Returns:
        Response:
            - Redirect to `next` URL.
    """
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
        old_path = os.path.join(
            current_app.config['PROFILE_PHOTO_FOLDER'], 
            old
        )
        if os.path.exists(old_path):
            os.remove(old_path)

    save_path = os.path.join(
        current_app.config['PROFILE_PHOTO_FOLDER'], 
        filename
    )
    photo.save(save_path)

    current_user.profile_photo = filename
    db.session.commit()

    return redirect(request.form.get('next'))