# The database for this application was developed with the support of Miguel 
# Grinberg's The Flash Mega Tutorial series
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

"""Data model definitions for Vision Hub.

    All models are defined using SQLAlchemy ORM and represent the database schema 
    for the application.

    Models include:
        - User: Represents a user in the system with self-referential 
        relationships for managers.
        - Role: Represents user roles (e.g., admin, manager, staff).
        - Department: Represents departments within the organization.
        - TrainingModule: Represents training modules with associated 
        questions and user progress.
        - Question: Represents questions within training modules.
        - Option: Represents answer options for questions.
        - UserModuleProgress: Tracks user progress in training modules.
        - UserQuestionAnswer: Represents answers submitted by users to questions.
        - OnboardingPath: Represents onboarding paths for different staff types.
        - OnboardingStep: Represents steps in an onboarding path, such as 
        training modules.
        - DocumentRepository: Represents documents in the repository.
        - Report: Represents reports generated in the system.
""" 
from datetime import datetime, timezone
from typing import Optional, List

from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import Boolean
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class User(UserMixin, db.Model):
    """
    Represents a user in the system.
    
    Attributes:
        id (int): Primary key.
        username (str): Unique login identifier (email).
        first_name (str): The user's first name.
        surname (str): The user's last name.
        job_title (str): The user's position title.
        password_hash (str): Hashed password for authentication.
        is_onboarding (bool): Flag indicating whether the user is in onboarding.
        dateStarted (datetime): Timestamp when the user account was created.
        google_email (Optional[str]): Optional linked Google account email.
        profile_photo (Optional[str]): Optional profile photo filename.
        manager_id (Optional[int]): Foreign key to another User (their manager).
        manager (User): The user's manager (self-referential relationship).
        manages (list[User]): List of users managed by this user.
        role_id (int): Foreign key to the Role model.
        role (Role): The role assigned to the user.
        department_id (int): Foreign key to the Department model.
        department (Department): The department assigned to the user.
        module_progress (list[UserModuleProgress]): List of training module 
            progress entries for this user.
        onboarding_path_id (Optional[int]): Foreign key to an OnboardingPath.
        onboarding_path (OnboardingPath): The onboarding path assigned to the user.
    """
    __tablename__ = 'user'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key = True)

    # User details
    username: so.Mapped[str] = so.mapped_column(
        sa.String(120), 
        index = True, 
        unique = True
    )
    first_name: so.Mapped[str] = so.mapped_column(
        sa.String(50), 
        index = True
    )
    surname: so.Mapped[str] = so.mapped_column(
        sa.String(50), 
        index = True
    )
    job_title: so.Mapped[str] = so.mapped_column(
        sa.String(50), 
        index = True
    )
    password_hash: so.Mapped[str] = so.mapped_column(
        sa.String(256)
    )
    is_onboarding: so.Mapped[bool] = so.mapped_column(
        default = False   # Default: Not onboarding
    )  
    dateStarted: so.Mapped[datetime] = so.mapped_column(
        index=True, 
        default = lambda: 
            datetime.now(timezone.utc)
    )
    google_email: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(120), 
        unique = True, 
        nullable = True
    )
    profile_photo: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(120), 
        nullable = True, 
        default = 'profileDefault.png'
    )

    # Self-referential relationship for manager and those managed
    manager_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('user.id'), 
        nullable = True
    )
    manager: so.Mapped[Optional['User']] = so.relationship(
        'User', 
        remote_side=[id], 
        back_populates = 'manages'
    )
    manages: so.Mapped[List['User']] = so.relationship(
        'User', 
        back_populates = 'manager'
    )

    # Relationship to role
    role_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('role.id')
    )
    role: so.Mapped['Role'] = so.relationship(
        'Role', 
        back_populates = 'users'
    )

    # Relationship to department
    department_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('department.id')
    )
    department: so.Mapped['Department'] = so.relationship(
        'Department', 
        back_populates = 'users'
    )

    # Relationship to module progress
    module_progress: so.Mapped[List['UserModuleProgress']] = so.relationship(
        'UserModuleProgress', back_populates = 'user'
    )

    # Relationship to onboarding path
    onboarding_path_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('onboarding_path.id'), 
        nullable = True
    )
    onboarding_path: so.Mapped['OnboardingPath'] = so.relationship(
        'OnboardingPath'
    )

    def __repr__(self):
        """Returns a string representation of the User object."""
        return f'<User {self.username}>'

    def set_password(self, password):
        """Sets the user's password by hashing it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the user's password matched the stored hashed password."""
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    """Loads a user by their ID for Flask-Login session management.

    Args:
        id (int): The unique identifier of the user.
        
    Returns:
        User: The User object or None if not found.
    """
    return db.session.get(User, int(id))


class Role(db.Model):
    """Represents a role in the system.
    
    Attributes:
        id (int): Primary key.
        role_name (str): Name of the role (e.g., admin, manager, staff).
        users (list[User]): List of users assigned to this role (relationship).
    """
    __tablename__ = 'role'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Role details
    role_name: so.Mapped[str] = so.mapped_column(
        sa.String(20), 
        index = True, 
        unique = True
    )

    # Relationship to User
    users: so.Mapped[list['User']] = so.relationship(
        'User', back_populates = 'role'
    )

    def __repr__(self):
        """Returns a string representation of the Role object."""
        return f'<Role {self.role_name}>'


class Department(db.Model):
    """Represents a department in the system.
    
    Attributes:
        id (int): Primary key.
        department_name (str): Name of the department (e.g., office, operational).
        users (list[User]): List of users assigned to this department.
    """
    __tablename__ = 'department'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(
        primary_key = True
    )

    # Department details
    department_name: so.Mapped[str] = so.mapped_column(
        sa.String(20), 
        index = True, 
        unique = True
    )

    # Relationship to User 
    users: so.Mapped[List['User']] = so.relationship(
        'User', 
        back_populates = 'department'
    )

    def __repr__(self):
        """Returns a string representation of the Department object."""
        return f'<Department {self.department_name}>'
    

class TrainingModule (db.Model):    
    """Represents a training module in the system.

    Attributes:
        id (int): Primary key.
        module_title (str): Title of the module.
        module_description (str): Detailed description.
        module_instructions (str): Instructions for completing the module.
        video_url (Optional[str]): Optional URL for video content.
        active (bool): Indicates whether the module is currently active.
        questions (list[Question]): Questions associated with the module.
        user_progress (list[UserModuleProgress]): Progress entries for users.
        onboarding_steps (List[OnboardingStep]): Steps in assigned onboarding 
            paths.
    """ 
    __tablename__ = 'training_module'   

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Training module details
    module_title: so.Mapped[str] = so.mapped_column(
        sa.String(150), index=True, unique=True
    )
    module_description: so.Mapped[str] = so.mapped_column(
        sa.Text, nullable=False
    )
    module_instructions: so.Mapped[str] = so.mapped_column(
        sa.Text, nullable=False
    )
    video_url: so.Mapped[str] = so.mapped_column(
        sa.String(300), nullable=True
    )
    active: so.Mapped[bool] = so.mapped_column(
        sa.Boolean, nullable=False, default=True
    )

    # Relationship with questions   
    questions: so.Mapped[List['Question']] = so.relationship(
        'Question', 
        back_populates = 'training_module', 
        cascade = 'all, delete-orphan')

    # Relationship with user progress
    user_progress: so.Mapped[List['UserModuleProgress']] = so.relationship(
        'UserModuleProgress', 
        back_populates = 'training_module'
    )

    # Relationship with onboarding steps
    onboarding_steps: so.Mapped[List['OnboardingStep']] = so.relationship(
        'OnboardingStep', 
        back_populates = 'training_module',
        cascade = 'all, delete-orphan'
        )

    def __repr__(self):
        """Returns a string representation of the TrainingModule object."""
        return f'<TrainingModule {self.module_title}>'


class Question (db.Model):
    """Represents a question in the system.

    Attributes:
        id (int): Primary key.
        question_text (str): The text of the question.
        training_module_id (int): Foreign key to TrainingModule.
        training_module (TrainingModule): Associated training module.
        options (list[Option]): List of answer choices for this question.
    """
    __tablename__ = 'question'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Question details
    question_text: so.Mapped[str] = so.mapped_column(
        sa.String(1000), 
        nullable=False
    )
    
    # Relationship with training module id
    training_module_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('training_module.id'), 
        nullable=False
    )
    training_module: so.Mapped['TrainingModule'] = so.relationship(
        'TrainingModule', 
        back_populates = 'questions')

    # Relationship with options
    options: so.Mapped[List['Option']] = so.relationship(
        'Option', 
        back_populates = 'question', 
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        """Returns a string representation of the Question object."""
        return f'<Question {self.question_text}>'


class Option (db.Model):
    """Represents answer options for a question.

    Attributes:
        id (int): Primary key.
        question_id (int): Foreign key to the question.
        option_text (str): The text of this option.
        is_correct (bool): True if this option is the correct answer.
        question (Question): The associated question.
    """
    __tablename__ = "option"

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Option details
    question_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('question.id'), 
        nullable=False
    )
    option_text: so.Mapped[str] = so.mapped_column(
        sa.String(500), 
        nullable=False
    )
    is_correct: so.Mapped[bool] = so.mapped_column(
        sa.Boolean, 
        default=False, 
        nullable=False
    )

    # Relationship with question
    question: so.Mapped['Question'] = so.relationship(
        'Question', 
        back_populates = 'options'
    )

    def __repr__(self):
        """Returns a string representation of the Option object."""
        return f'<Option {self.option_text}>'


class UserModuleProgress (db.Model):
    """
    Represents the progress of a user in a training module.

    Attributes:
        id (int): Primary key.
        start_date (datetime): When the module was started.
        completed_date (datetime, optional): When the module was completed.
        score (int, optional): The score achieved by the user in the module.
        attempts (int): Number of attempts made by the user.
        user_id (int): Foreign key to the User model.
        user (User): The user associated with this progress entry.
        training_module_id (int): Foreign key to the TrainingModule model.
        training_module (TrainingModule): The training module associated with 
            this progress entry.
        answers (list[UserQuestionAnswer]): Answers submitted during this attempt.
    """
    __tablename__ = 'user_module_progress'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True) 

    # User Module Progress details
    start_date: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, 
        default = lambda: datetime.now(timezone.utc), 
        nullable = False
    )
    completed_date: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, 
        nullable = True
    )
    score: so.Mapped[int] = so.mapped_column(
        sa.Integer, 
        nullable = True
    )
    attempts: so.Mapped[int] = so.mapped_column(
        sa.Integer, 
        default=0, 
        nullable = False
    )

    # Relationship to User
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user.id'), 
        nullable = False
    )
    user: so.Mapped['User'] = so.relationship(
        'User', 
        back_populates = 'module_progress'
    )

    # Relationship to Training Module
    training_module_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('training_module.id'), 
        nullable = False
    )
    training_module: so.Mapped['TrainingModule'] = so.relationship(
        'TrainingModule', 
        back_populates = 'user_progress'
    )

    # Relationship to User Question Answer
    answers: so.Mapped[List['UserQuestionAnswer']] = so.relationship(
        'UserQuestionAnswer', 
        back_populates = 'progress', 
        cascade = 'all, delete-orphan'
    )


class UserQuestionAnswer (db.Model):
    """Represents an answer submitted by a user to a specific question.

    Attributes:
        id (int): Primary key.
        is_correct (bool): True if the selected option was correct.
        progress_id (int): Foreign key to the UserModuleProgress model.
        progress (UserModuleProgress): Relationship to the user's progress 
            record.
        question_id (int): Foreign key to the Question.
        question (Question): Question associated with this answer.
        selected_option_id (int, optional): Foreign key to the chosen Option.
        selected_option (Option, optional): Relationship to the selected 
            Option (if any).
    """
    __tablename__ = 'user_question_answer'
    
    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean)
    
    # User Question Answer details
    progress_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user_module_progress.id'), 
        nullable = False
    )

    # Relationship to User Module Progress
    progress: so.Mapped['UserModuleProgress'] = so.relationship(
        'UserModuleProgress', 
        back_populates = 'answers'
    )

    # Relationship to question
    question_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('question.id'), 
        nullable = False
    )
    question: so.Mapped['Question'] = so.relationship('Question')
    
    # Relationship to option
    selected_option_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('option.id'), 
        nullable = True
    )
    selected_option: so.Mapped['Option'] = so.relationship('Option')


class OnboardingPath(db.Model):
    """Represents an onboarding path defining a sequence of steps for staff.

    Attributes:
        id (int): Primary key.
        path_name (str): Name of the onboarding path (e.g., “office”, 
            “operational”).
        steps (list[OnboardingStep]): Ordered steps in this path.
    """
    __tablename__ = 'onboarding_path'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    #Onboarding path details
    path_name: so.Mapped[str] = so.mapped_column(
        sa.String(100), 
        nullable=False, 
        unique=True
    )

    # Relationship with onboarding steps
    steps: so.Mapped[List['OnboardingStep']] = so.relationship(
        'OnboardingStep', 
        back_populates='path', 
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        """Returns a string representation of the Onboarding Path object."""
        return f"<OnboardingPath {self.path_name}>"
    

class OnboardingStep(db.Model):
    """Step within an onboarding path, e.g. a training module or task.
    
    Attributes:
        id (int): Primary key.
        step_name (str): Name of this step.
        onboarding_path_id (int): Foreign key to the OnboardingPath.
        path (OnboardingPath): Relationship back to the parent path.
        training_module_id (int, optional): Foreign key to the TrainingModule, 
            if any.
        training_module (TrainingModule): The training module associated with 
            this step.
    """
    __tablename__ = 'onboarding_step'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key = True)

    # Onboarding Step details
    step_name: so.Mapped[str] = so.mapped_column(
        sa.String(150), 
        nullable = False
    )
    
    # Relationship to Onboarding Path
    onboarding_path_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('onboarding_path.id'), 
        nullable = False
    )
    path: so.Mapped['OnboardingPath'] = so.relationship(
        'OnboardingPath', 
        back_populates = 'steps'
    )

    # Relationship to training modules
    training_module_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('training_module.id'), 
        nullable = True
    )
    training_module: so.Mapped['TrainingModule'] = so.relationship(
        'TrainingModule', 
        back_populates = 'onboarding_steps'
    )

    def __repr__(self):
        """Returns a string representation of the OnboardingStep object."""
        return f"<OnboardingStep {self.step_name}>"
    

class DocumentRepository(db.Model):
    """Represents a document in the repository.

    Attributes:
        id (int): Primary key.
        document_title (str): Title of the document.
        document_category (str): Category of the document (e.g., Policy, Guide, 
            Form).
        upload_date (datetime): Timestamp when uploaded.
        file_path (str):  Filesystem path to the uploaded file.
        user_id (int): Foreign key to the uploaders User model.
        uploaded_by_user (User): The user who uploaded the document.
    """
    __tablename__ = 'document_repository'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Repository details
    document_title: so.Mapped[str] = so.mapped_column(
        sa.String(150), 
        nullable = False
    )
    document_category: so.Mapped[str] = so.mapped_column(
        sa.Enum('Policy', 'Guide', 'Form', 
        name = 'document_category'), 
        nullable = False
    )
    upload_date: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable = False
    )
    file_path: so.Mapped[str] = so.mapped_column(
        sa.String(300), 
        nullable = False
    )

    # Relationship to User
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('user.id'), 
        nullable = False
    )
    uploaded_by_user: so.Mapped['User'] = so.relationship('User')

    def __repr__(self):
        """Returns a string representation of the Document Repository object."""
        return f"<DocumentRepository {self.document_title}>"

    
class Report(db.Model):
    """Represents a report in the system.
    
    Attributes:
        id (int): Primary key.
        report_type (str): Type of report (e.g., Completion, Performance).
        description (str): Short description of the report.
        report_data (str, optional): Stored Json report content.
        created_at (datetime): Timestamp when the report was created.
    """
    __tablename__ = 'report'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Report details
    report_type: so.Mapped[str] = so.mapped_column(
        sa.Enum('Completion', 'Performance', name = 'report_type'), 
        nullable = False
    )
    description: so.Mapped[str] = so.mapped_column(
        sa.String(255), 
        nullable = False
        )    
    report_data: so.Mapped[Optional[str]] = so.mapped_column(
        sa.Text, 
        nullable = True)  
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, 
        default = lambda: datetime.now(timezone.utc), 
        nullable = False
    )

    def __repr__(self):
        """Returns a string representation of the Report object."""
        return f"<Report {self.report_type} created on {self.created_at}>"