from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User


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
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[(1, 'Admin'), (2, 'Manager'), (3, 'Staff')],  coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register')

