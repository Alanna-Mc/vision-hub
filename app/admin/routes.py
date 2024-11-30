from app import app, db
from app.admin.forms import CreateUserForm, EditUserForm
from app.models import User, Role, Department
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from datetime import datetime

@app.route('/admin/register', methods=['GET', 'POST'])
def register_user():
    if not current_user.is_authenticated or current_user.role.role_name != 'Admin':
        return redirect(url_for('logout'))

    form = CreateUserForm()

    # Set dropdown values for non-text fields
    form.role.choices = [(0, 'Select Role')] + [(role.id, role.role_name) for role in Role.query.all()]
    form.department.choices = [(0, 'Select Department')] + [(dept.id, dept.department_name) for dept in Department.query.all()]
    form.manager.choices = [(0, 'None')] + [(user.id, f"{user.first_name} {user.surname}") for user in User.query.all()]

    # Form data
    if form.validate_on_submit():
        # Create a new user instance
        user = User(
            first_name=form.firstName.data,
            surname=form.surname.data,
            username=form.username.data,
            role_id=int(form.role.data),
            is_onboarding=(form.is_onboarding.data == 'yes'),
            manager_id=int(form.manager.data) if form.manager.data else None,
            department_id=int(form.department.data),
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
    if current_user.role.role_name!= "Admin":
        return redirect(url_for('logout'))
    return render_template('admin/dashboard.html', title='Admin Dashboard')


@app.route('/admin/manage_users', methods=['GET'])
@login_required
def manage_users():
    if current_user.role.role_name != "Admin":
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
    if current_user.role.role_name != "Admin":
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

