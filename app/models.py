# The database for this application was developed with the support of Miguel Grinberg's The Flash Mega Tutorial series
 
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, List
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
    manager: so.Mapped[Optional['User']] = so.relationship('User', remote_side=[id], back_populates='manages')
    manages: so.Mapped[List['User']] = so.relationship('User', back_populates='manager')
    # Foreign key to Role 
    role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('role.id'))
    role: so.Mapped['Role'] = so.relationship('Role', back_populates='users')
    # Foreign key to Department 
    department_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('department.id'))
    department: so.Mapped['Department'] = so.relationship('Department', back_populates='users')
    dateStarted: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    job_title: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    module_progress: so.Mapped[List['UserModuleProgress']] = so.relationship('UserModuleProgress', back_populates='user')

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
    users: so.Mapped[list['User']] = so.relationship('User', back_populates='role')
    
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
    users: so.Mapped[List['User']] = so.relationship('User', back_populates='department')
    
    def __repr__(self):
        """
        Returns a string representation of the Department object.

        Returns:
            str: A formatted string containing the department name.
        """
        return f'<Department {self.department_name}>'
    

class TrainingModule (db.Model):     
    __tablename__ = 'training_module'   
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    module_title: so.Mapped[str] = so.mapped_column(sa.String(150), index=True, unique=True)
    module_description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    module_instructions: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    video_url: so.Mapped[str] = so.mapped_column(sa.String(300))
        
    questions: so.Mapped[List['Question']] = so.relationship('Question', back_populates='training_module', cascade='all, delete-orphan')
    user_progress: so.Mapped[List['UserModuleProgress']] = so.relationship('UserModuleProgress', back_populates='training_module')


class Question (db.Model):
    __tablename__ = 'question'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    question_text: so.Mapped[str] = so.mapped_column(sa.String(1000), nullable=False)
    
    training_module_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('training_module.id'), nullable=False)
    training_module: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='questions')

    options: so.Mapped[List['Option']] = so.relationship('Option', back_populates='question', cascade='all, delete-orphan')


class Option (db.Model):
    __tablename__ = "option"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('question.id'), nullable=False)
    option_text: so.Mapped[str] = so.mapped_column(sa.String(500), nullable=False)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)

    question: so.Mapped['Question'] = so.relationship('Question', back_populates='options')


class UserModuleProgress (db.Model):
    __tablename__ = 'user_module_progress'
    id: so.Mapped[int] = so.mapped_column(primary_key=True) 
    start_date: so.Mapped[datetime] = so.mapped_column(
    sa.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    attempts: so.Mapped[int] = so.mapped_column(sa.Integer, default=0, nullable=False)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    user: so.Mapped['User'] = so.relationship('User', back_populates='module_progress')
    
    training_module_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('training_module.id'), nullable=False)
    training_module: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='user_progress')
    
    answers: so.Mapped[List['UserQuestionAnswer']] = so.relationship('UserQuestionAnswer', back_populates='progress', cascade='all, delete-orphan')


class UserQuestionAnswer (db.Model):
    __tablename__ = 'user_question_answer'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean)
    
    progress_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user_module_progress.id'), nullable=False)
    progress: so.Mapped['UserModuleProgress'] = so.relationship('UserModuleProgress', back_populates='answers')
    
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('question.id'), nullable=False)
    question: so.Mapped['Question'] = so.relationship('Question')

    selected_option_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('option.id'), nullable=True)
    selected_option: so.Mapped['Option'] = so.relationship('Option')