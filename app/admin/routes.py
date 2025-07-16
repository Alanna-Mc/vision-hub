from app import app, db
from app.admin.forms import CreateUserForm, EditUserForm, CreateTrainingModuleForm
from app.models import User, Role, Department, TrainingModule, Question, Option, OnboardingPath, OnboardingStep
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


@app.route('/admin/view_user/<int:user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))

    user = User.query.get_or_404(user_id)

    return render_template('admin/viewUser.html', title='View User', user=user)


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

        #flash(f'User {user.first_name} {user.surname} user details have been updated')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/editUser.html', title='Edit User', form=form, user=user)


@app.route('/admin/create_training_module', methods=['GET', 'POST'])
@login_required
def create_training_module():
    if current_user.role.role_name != "admin":
        return redirect(url_for('logout'))

    form = CreateTrainingModuleForm()

    form.pathways.choices = [(path.id, path.path_name) for path in OnboardingPath.query.all()]

    # Check if the user wants to add another question
    if request.method == 'POST' and 'add_question' in request.form:
        # Add another empty question to the FieldList
        form.questions.append_entry()
        # Re-render the form with the new question included
        return render_template('admin/create_training_module.html', title='Create Training Module', form=form)

    if form.validate_on_submit():
        try:
            # Create the training module
            training_module = TrainingModule(
                module_title=form.module_title.data,
                module_description=form.module_description.data,
                module_instructions=form.module_instructions.data,
                video_url=form.video_url.data or None
                )
            db.session.add(training_module)
            db.session.flush()

            # Assign module to selected pathways
            for pathway_id in form.pathways.data:
                pathway = OnboardingPath.query.get(pathway_id)
                if pathway:
                    onboarding_step = OnboardingStep(
                        step_name=training_module.module_title,
                        path=pathway,
                        training_module=training_module
                    )
                    db.session.add(onboarding_step) 
            
            # Ensure at least one question is provided
            if not form.questions.data or len(form.questions.data) < 1:
                flash("You must add at least one question for the training module.")
                db.session.rollback()
                return redirect(url_for('create_training_module'))
            
            # Create questions and options
            for question_form in form.questions:
                question = Question(
                    question_text=question_form.question_text.data,
                    training_module=training_module
                )
                db.session.add(question)
                db.session.flush()

                for option_form in [question_form.option1, question_form.option2, question_form.option3, question_form.option4]:
                    option = Option(
                        option_text=option_form.option_text.data,
                        is_correct=option_form.is_correct.data,
                        question=question
                    )
                    db.session.add(option)

            # Save everything to the database
            db.session.commit()  
            flash(f'Training module "{training_module.module_title}" has been successfully created!')
            return redirect(url_for('admin_dashboard'))
    
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}')
            return redirect(url_for('create_training_module'))
    else:
        print("Form errors:", form.errors)
        flash("There are errors in your form submission.")

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
