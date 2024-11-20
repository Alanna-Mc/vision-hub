from app import app, db
from app.admin.forms import CreateUserForm
from app.models import User, Role
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

@app.route('/admin/register', methods=['GET', 'POST'])
def register_user():
    if not current_user.is_authenticated or current_user.role.role_name != 'Admin':
        flash("You are not authorized to access this page.")
        return redirect(url_for('index'))

    form = CreateUserForm()
    if form.validate_on_submit():
        # Create a new user instance
        user = User(
            first_name=form.firstName.data,
            surname=form.surname.data,
            username=form.username.data,
            role_id=int(form.role.data)
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.first_name} {user.surname} has been successfully registered!')
        return redirect(url_for('index'))

    return render_template('admin/createUser.html', title='Register User', form=form)


@app.route('/manage_users', methods=['GET'])
def manage_users():
    return render_template('admin/manageUsers.html', title='Manage Users')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role.role_name!= "Admin":
        return redirect(url_for('index'))
    return render_template('admin/dashboard.html', title='Admin Dashboard')