from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sai
from app import db
from app.models import User

class CreateUserForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField(
        'Role', 
        choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Staff', 'Staff')],
        validators=[DataRequired()]
    submit = SubmitField('Register')
