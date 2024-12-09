from app import app, db
from app.admin.forms import CreateUserForm, EditUserForm, CreateTrainingModuleForm
from app.models import User, Role, Department, TrainingModule, Question, Option, OnboardingPath
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from datetime import datetime

@app.route('/admin/register', methods=['GET', 'POST'])
def register_user():
    if not current_user.is_authenticated or current_user.role.role_name != 'admin':
        return redirect(url_for('logout'))

    form = CreateUserForm()

    # Set dropdown values for non-text fields
    form.role.choices = [(0, 'Select Role')] + [(role.id, role.role_name) for role in Role.query.all()]
    form.department.choices = [(0, 'Select Department')] + [(dept.id, dept.department_name) for dept in Department.query.all()]
    form.manager.choices = [(0, 'None')] + [(user.id, f"{user.first_name} {user.surname}") for user in User.query.all()]

    # Form data
    if form.validate_on_submit():

        # Determine the onboarding path based on the department
        department_id = int(form.department.data)
        if Department.query.filter_by(id=department_id, department_name="office").first():
            onboarding_path = OnboardingPath.query.filter_by(path_name="office staff").first()
        else:
            onboarding_path = OnboardingPath.query.filter_by(path_name="operational staff").first()
       
        # Create a new user instance
        user = User(
            first_name=form.firstName.data,
            surname=form.surname.data,
            username=form.username.data,
            role_id=int(form.role.data),
            is_onboarding=(form.is_onboarding.data == 'yes'),
            manager_id=int(form.manager.data) if form.manager.data else None,
            department_id=int(form.department.data),
            onboarding_path_id=onboarding_path.id if onboarding_path else None,
            dateStarted= datetime.now(),
            job_title=form.job_title.data
        )

        # Set password
        user.set_password(form.password.data)
        # Save the user to the database
        db.session.add(user)
        db.session.commit()
        # User confirmation
        flash(f'User {user.first_name} {user.surname} has been successfully registered!')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/createUser.html', title='Register User', form=form)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role.role_name!= "admin":
        return redirect(url_for('logout'))
    return render_template('admin/dashboard.html', title='Admin Dashboard')


@app.route('/admin/manage_users', methods=['GET'])
@login_required
def manage_users():
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))
     
    try:
        users = User.query.all()
        return render_template('admin/manageUsers.html', title='Manage Users', users = users)
    except Exception as e:
        error_message = 'Error: ' + str(e)
        return error_message


@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))
    
    # Retrieve the user to edit
    user = User.query.get_or_404(user_id)

    # Set dropdown values for non-text fields
    role_choices = [(role.id, role.role_name) for role in Role.query.all()]
    department_choices = [(dept.id, dept.department_name) for dept in Department.query.all()]
    manager_choices = [(0, 'None')] + [(manager.id, f"{manager.first_name} {manager.surname}") for manager in User.query.all()]

    # Fill the text fields with the user's data
    form = EditUserForm(obj=user)
  
    # Assign dropdown choices to form fields
    form.role.choices = role_choices
    form.department.choices = department_choices
    form.manager.choices = manager_choices
    
    # Set user values to dropdown fields
    form.role.data = user.role_id
    form.department.data = user.department_id
    form.manager.data = user.manager_id or 0  # Use 0 if manager_id is None
    form.is_onboarding.data = 'yes' if user.is_onboarding else 'no'

    # Form data
    if form.validate_on_submit():
        # Update user details
        user.first_name=form.first_name.data,
        user.surname=form.surname.data,
        user.username=form.username.data,
        user.role_id=int(form.role.data),
        user.is_onboarding=(form.is_onboarding.data == 'yes'),
        user.manager_id=int(form.manager.data) if form.manager.data else None,
        user.department_id=int(form.department.data),
        user.job_title=form.job_title.data

        # Password reset optional
        if form.password.data:
            user.set_password(form.password.data)

        # Start date update optional
        if form.dateStarted.data:
            user.dateStarted = form.dateStarted.data

        # Save changes to the database
        db.session.commit()

        flash(f'User {user.first_name} {user.surname} user details have been updated')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/editUser.html', title='Edit User', form=form, user=user)


@app.route('/admin/create_training_module', methods=['GET', 'POST'])
@login_required
def create_training_module():
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))

    form = CreateTrainingModuleForm()

    if form.validate_on_submit():
        # Create the training module
        training_module = TrainingModule(
            module_title=form.module_title.data,
            module_description=form.module_description.data,
            module_instructions=form.module_instructions.data,
            video_url=form.video_url.data or None
        )
        db.session.add(training_module)
        db.session.flush()  # Save the module and get its ID

        # Create questions and their options
        for question_form in form.questions:
            question = Question(
                question_text=question_form.question_text.data,
                training_module=training_module
            )
            db.session.add(question)
            db.session.flush()  # Save the question and get its ID

            # Add options
            for option_form in question_form.options:
                option = Option(
                    option_text=option_form.option_text.data,
                    is_correct=option_form.is_correct.data,
                    question=question
                )
                db.session.add(option)
        
        db.session.commit()  # Save everything to the database
        flash(f'Training module "{training_module.module_title}" has been successfully created!')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_training_module.html', title='Create Training Module', form=form)


@app.route('/admin/manage_training_modules', methods=['GET'])
@login_required
def manage_training_modules():
    # Ensure only admins can access this page
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))
    
    # Fetch all training modules
    modules = TrainingModule.query.all()
    
    # Render the template with the modules
    return render_template(
        'admin/manage_training_modules.html',
        title='Manage Training Modules',
        modules=modules
    )

@app.route('/admin/details_training_module/<int:module_id>', methods=['GET'])
@login_required
def details_training_module(module_id):
    # Ensure only admins can access this page
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))
    
    # Fetch the specific training module
    module = TrainingModule.query.get_or_404(module_id)
    
    # Fetch questions related to the module
    questions = Question.query.filter_by(training_module_id=module_id).all()
    
    return render_template(
        'admin/details_training_module.html', 
        title=f'{module.module_title} Details',
        module=module,
        questions=questions
    )
