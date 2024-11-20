from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Optional
import sqlalchemy as sa
from app import db
from app.models import User, Department, Role


def validate_email(self, field):
    value = field.data
    if '@' not in value or '.' not in value.split('@')[-1]:
        raise ValidationError('Invalid email address.')

 
def validate_username(self, username):
    user = db.session.scalar(sa.select(User).where( User.username == username.data))
    if user is not None:
        raise ValidationError('Email address already registered.')


class CreateUserForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Email', validators=[DataRequired(), validate_email, validate_username])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_onboarding = RadioField('Does staff memeber need onboarding?', choices=[('yes', 'Yes'), ('no', 'No')],validators=[DataRequired()])
    manager= SelectField('Manager', coerce=int, validators=[Optional()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    job_title = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Register')
    
