from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField, DateField, TextAreaField, URLField, FormField, FieldList, BooleanField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Optional, URL, Length
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
    is_onboarding = RadioField('Does staff member need onboarding?', choices=[('yes', 'Yes'), ('no', 'No')],validators=[DataRequired()])
    manager= SelectField('Manager', coerce=int, validators=[Optional()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    job_title = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Register')


class EditUserForm(FlaskForm):
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
    submit = SubmitField('Edit Details')


class QuestionForm(FlaskForm):
    question_text = TextAreaField("Question Text", validators=[DataRequired(), Length(max=1000)])
    options = FieldList(FormField(
            type('OptionForm', (FlaskForm,), {
                'option_text': StringField("Option Text", validators=[DataRequired(), Length(max=500)]),
                'is_correct': BooleanField("Is Correct")
            })
        ), 
        min_entries=2, 
        max_entries=4
    )

    
class CreateTrainingModuleForm(FlaskForm):
    module_title = StringField("Module Title", validators=[DataRequired(), Length(max=150)])
    module_description = TextAreaField("Description", validators=[DataRequired()])
    module_instructions = TextAreaField("Instructions", validators=[DataRequired()])
    video_url = URLField("Video URL (Optional)", validators=[Optional(), URL(require_tld=True), Length(max=300)])
    questions = FieldList(FormField(QuestionForm), min_entries=1, max_entries=20)
    submit = SubmitField("Create Training Module")


