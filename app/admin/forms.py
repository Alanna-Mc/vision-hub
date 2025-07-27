"""Flask-WTF admin form definitions for Vision Hub application."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField, DateField, TextAreaField, URLField, FormField, FieldList, BooleanField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Optional, URL, Length
import sqlalchemy as sa

from app import db
from app.models import User, Department, Role


def validate_email(self, field):
    """Validator to check if the email is valid."""
    value = field.data
    if '@' not in value or '.' not in value.split('@')[-1]:
        raise ValidationError('Invalid email address.')

 
def validate_username(self, field):
    """Validator to check if the username is already registered."""
    existing = db.session.scalar(
        sa.select(User).where(User.username == field.data)
    )
    if existing and existing.id != getattr(self, 'user_id', None):
        raise ValidationError('Email address already registered.')


class CreateUserForm(FlaskForm):
    """Form for creating a new user in the admin interface."""
    firstName = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Email', validators=[DataRequired(), validate_email, validate_username])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_onboarding = RadioField('Does staff member need onboarding?', choices=[('yes', 'Yes'), ('no', 'No')],validators=[DataRequired()])
    manager= SelectField('Manager', coerce=int, validators=[Optional()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    job_title = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Register')


class EditUserForm(FlaskForm):
    """Form for editing an existing user in the admin interface."""
    first_name = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Email', validators=[DataRequired(), validate_email, validate_username])
    password = PasswordField('Password Reset', validators=[Optional()])
    password2 = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('password')])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_onboarding = RadioField('Does staff member need onboarding?', choices=[('yes', 'Yes'), ('no', 'No')],validators=[DataRequired()])
    manager= SelectField('Manager', coerce=int, validators=[Optional()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    job_title = StringField('Position', validators=[DataRequired()])
    dateStarted = DateField('Start Date', format='%d-%m-%y', validators=[Optional()])
    submit = SubmitField('Confirm')             


class OptionForm(FlaskForm):
    """Sub-form for creating or editing an option in a question."""
    option_text = StringField("Option Text", validators=[DataRequired(), Length(max=500)])
    is_correct = BooleanField("Correct Answer")

    class Meta:
        csrf = False

class QuestionForm(FlaskForm):
    """Sub-form for a quiz question; contains four OptionForm fields."""
    question_text = TextAreaField("Question Text", validators=[DataRequired(), Length(max=1000)])
    option1 = FormField(OptionForm)
    option2 = FormField(OptionForm)
    option3 = FormField(OptionForm)
    option4 = FormField(OptionForm)

    class Meta:
        csrf = False

class CreateTrainingModuleForm(FlaskForm):
    """Admin form to build a TrainingModule with questions and pathways."""
    module_title = StringField("Module Title", validators=[DataRequired(), Length(max=150)])
    module_description = TextAreaField("Description", validators=[DataRequired()])
    module_instructions = TextAreaField("Instructions", validators=[DataRequired()])
    video_url = URLField("Video URL (Optional)", validators=[Optional(), URL(require_tld=True), Length(max=300)])
    pathways = SelectMultipleField("Assign to Pathways", coerce=int, validators=[DataRequired()])
    questions = FieldList(FormField(QuestionForm), min_entries=1, max_entries=20)
    submit = SubmitField("Create")

