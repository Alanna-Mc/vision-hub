# The database for this application was developed with the support of Miguel Grinberg's The Flash Mega Tutorial series
 
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login


class User(UserMixin, db.Model):
    """
    Represents a user in the system.
    
    Attributes:
       id (int): The unique identifier for the user (primary key).       
       username (str): The user's email address, must be unique.
       first_name (str): The user's first name.
       surname (str): The user's last name.
       password_hash (Optional[str]): The hashed password for the user.
       role_id (int): Foreign key linking to the Role model.
       role (Role): The role associated with the user (relationship).
       dateStarted (datetime): The time when the user was created.
    """
    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    surname: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    # Default: Not onboarding
    is_onboarding: so.Mapped[bool] = so.mapped_column(default=False)
    manager_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    manager: so.Mapped[Optional['User']] = so.relationship('User', remote_side=[id])
    # Foreign key to Role 
    role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('role.id'))
    role: so.Mapped['Role'] = so.relationship('Role', back_populates='users')
    # Foreign key to Department 
    department_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('department.id'))
    department: so.Mapped['Department'] = so.relationship('Department', back_populates='users')
    dateStarted: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    job_title: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    
    def __repr__(self):
        """
        Returns a string representation of the User object.

        Returns:
            str: A formatted string containing the username.
        """
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Role(db.Model):
    """
    Represents a role in the system.
    
    Attributes:
        id (int): The unique identifier for the role (primary key).
        role_name (str): The name of the role (e.g., Admin, Manager, Staff).
        users (list[User]): List of users assigned to this role (relationship).
    """
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    role_name: so.Mapped[str] = so.mapped_column(sa.String(20), index=True, unique=True)

    # Relationship to User model
    users: so.Mapped['User'] = so.relationship('User', back_populates='role', cascade='all, delete-orphan')
    
    def __repr__(self):
        """
        Returns a string representation of the Role object.

        Returns:
            str: A formatted string containing the role name.
        """
        return f'<Role {self.role_name}>'


class Department(db.Model):
    """
    Represents a department in the system.
    
    Attributes:
        id (int): The unique identifier for the role (primary key).
        department_name (str): The name of the department (e.g., office, operational).
        users (list[User]): List of users assigned to this role (relationship).
    """
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    department_name: so.Mapped[str] = so.mapped_column(sa.String(20), index=True, unique=True)

    # Relationship to User model
    users: so.Mapped['User'] = so.relationship('User', back_populates='department', cascade='all, delete-orphan')
    
    def __repr__(self):
        """
        Returns a string representation of the Department object.

        Returns:
            str: A formatted string containing the department name.
        """
        return f'<Department {self.department_name}>'
    

class TrainingModule (db.Model):        
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    module_title: so.Mapped[str] = so.mapped_column(sa.String(150), index=True, unique=True)
    module_description: so.Mapped[str] = so.mapped_column(sa.Text)
    module_instructions: so.Mapped[str] = so.mapped_column(sa.Text)
    video_url: so.Mapped[str] = so.mapped_column(sa.String(300))
        
    questions: so.Mapped[list['Question']] = so.relationship('Question', back_populates='training_module', cascade='all, delete-orphan')
    user_progress: so.Mapped[list['UserModuleProgress']] = so.relationship('UserModuleProgress', back_populates='training_module')


class Question (db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    trainingModule_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('trainingmodule.id'), nullable=False)
    question_text: so.Mapped[str] = so.mapped_column(sa.String(1000))

    trainingmodule: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='questions')
    options: so.Mapped[list['Option']] = so.relationship('Option', back_populates='question', cascade='all, delete-orphan')


class Option (db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('question.id'), nullable=False)
    option_text: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    question: so.Mapped['Question'] = so.relationship('Question', back_populates='options')


class UserModuleProgress (db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    module_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('module.id'), nullable=False)
    start_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    completed_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    attempts: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)

    user: so.Mapped['User'] = so.relationship('User', back_populates='module_progress')
    module: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='user_progress')
    answers: so.Mapped[list['UserQuestionAnswer']] = so.relationship('UserQuestionAnswer', back_populates='progress', cascade='all, delete-orphan')


class UserQuestionAnswer (db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    progress_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user_module_progress.id'), nullable=False)
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('question.id'), nullable=False)
    selected_option_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('option.id'), nullable=True)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean)

    progress: so.Mapped['UserModuleProgress'] = so.relationship('UserModuleProgress', back_populates='answers')
    question: so.Mapped['Question'] = so.relationship('Question')
    selected_option: so.Mapped['Option'] = so.relationship('Option')