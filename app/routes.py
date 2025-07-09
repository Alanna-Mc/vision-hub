import sqlalchemy as sa
import os
import secrets
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm
from app import app, db
from app.models import User, TrainingModule, UserModuleProgress, Option, UserQuestionAnswer
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone
from werkzeug.utils import UpdateProfilePhotoForm

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
    
    # Get the onboarding steps and training modules for the user's path
    onboarding_path = current_user.onboarding_path
    if onboarding_path:
        steps = onboarding_path.steps
    else:
        steps = []

    # Separate modules by status
    completed_modules = []
    to_be_completed_modules = []
    in_progress_modules = []

    # If module failed, use to identify as in progress rather than completed
    passing_threshold = 0.5

    for step in steps:
        module = step.training_module
        # Get the latest attempt
        if module:
            progress = UserModuleProgress.query.filter_by(
                user_id=current_user.id,
                training_module_id=module.id
            ).order_by(UserModuleProgress.id.desc()).first()

            # Determine status of current module
            # If no progress, it's "to be completed"
            if not progress:
                to_be_completed_modules.append(module)
            # If there is progress
            else:
                total_questions = len(module.questions) or 1  # Avoid division by zero
                # User finished at least one attempt
                if progress.completed_date:
                    # Check if this attempt passed
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

@app.route('/update_profile_photo', methods=['GET', 'POST'])
@login_required
def update_profile_photo():
    form = UpdateProfilePhotoForm()
    if form.validate_on_submit():
        if form.photo.data:
            while True:
                # Generate a secure filename and save the photo
                random_hex = secrets.token_hex(8)
                _, file_extension = os.path.splitext(secure_filename(form.photo.data.filename))
                photo_filename = random_hex + file_extension
                
                existing_user = User.query.filter_by(profile_photo=photo_filename).first()
                photo_path = os.path.join(app.root_path, 'static/images/profilePhoto', photo_filename)

                if not existing_user and not os.path.exists(photo_path):
                    break 
    
                # Overwrite users previously uploaded photo
                if current_user.profile_photo != 'profile_default.png':
                    old_photo_path = os.path.join(app.root_path, 'static/images/profilePhoto', current_user.profile_photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)

                # Save new photo
                form.photo.data.save(photo_path)

                # Update user in database
                current_user.profile_photo = photo_filename
                db.session.commit()
                flash('Your profile photo has been updated!', 'success')
                if current_user.role.role_name == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif current_user.role.role_name == 'manager':
                    return redirect(url_for('manager_dashboard'))
                elif current_user.role.role_name == 'staff':
                    return redirect(url_for('staff_dashboard'))

        return render_template('update_profile_photo.html', form=form)


  


