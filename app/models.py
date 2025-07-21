# The database for this application was developed with the support of Miguel Grinberg's The Flash Mega Tutorial series
 
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import Boolean
from app import db, login


class User(UserMixin, db.Model):
    """
    Represents a user in the system.
    
    Attributes:
        id (int): The unique identifier for the user (primary key).       
        username (str): The user's email address, must be unique.
        first_name (str): The user's first name.
        surname (str): The user's last name.
        job_title (str): The user's job title.
        password_hash (str): The hashed password for the user.
        is_onboarding (bool): Indicates whether the user is currently onboarding.
        dateStarted (datetime): The date and time when the user account was created.
        manager_id (int, optional): The ID of the manager assigned to the user.
        manager (User, optional): The manager (self-referential relationship).
        manages (list[User]): List of users managed by this user (self-referential relationship).
        role_id (int): The ID of the role assigned to the user.
        role (Role): The role assigned to the user (relationship to Role model).
        department_id (int): The ID of the department assigned to the user.
        department (Department): The department assigned to the user (relationship to Department model).
        module_progress (list[UserModuleProgress]): List of training module progress entries for this user.
        onboarding_path_id (int, optional): The ID of the onboarding path assigned to the user.
        onboarding_path (OnboardingPath, optional): The onboarding path assigned to the user.
       
    """
    __tablename__ = 'user'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # User details
    username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    surname: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    job_title: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    is_onboarding: so.Mapped[bool] = so.mapped_column(default=False) # Default: Not onboarding
    dateStarted: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    google_email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120), unique=True, nullable=True)
    profile_photo: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120), nullable=True, default='profileDefault.png')

    # Self-referential relationship for manager and those managed
    manager_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    manager: so.Mapped[Optional['User']] = so.relationship('User', remote_side=[id], back_populates='manages')
    manages: so.Mapped[List['User']] = so.relationship('User', back_populates='manager')
    
    # Relationship to role
    role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('role.id'))
    role: so.Mapped['Role'] = so.relationship('Role', back_populates='users')
    
    # Relationship to department
    department_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('department.id'))
    department: so.Mapped['Department'] = so.relationship('Department', back_populates='users')
   
    # Relationship to module progress
    module_progress: so.Mapped[List['UserModuleProgress']] = so.relationship('UserModuleProgress', back_populates='user')
   
    # Relationship to onboarding path
    onboarding_path_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('onboarding_path.id'), nullable=True)
    onboarding_path: so.Mapped['OnboardingPath'] = so.relationship('OnboardingPath')


    def __repr__(self):
        """
        Returns a string representation of the User object.
        """
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        Sets the user's password by hashing it.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifies the user's password matched the stored hashed password.
        """
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Role(db.Model):
    """
    Represents a role in the system.
    
    Attributes:
        id (int): The unique identifier for the role (primary key).
        role_name (str): The name of the role (e.g., admin, manager, staff).
        users (list[User]): List of users assigned to this role (relationship).
    """
    __tablename__ = 'role'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Role details
    role_name: so.Mapped[str] = so.mapped_column(sa.String(20), index=True, unique=True)

    # Relationship to User
    users: so.Mapped[list['User']] = so.relationship('User', back_populates='role')
    
    def __repr__(self):
        """
        Returns a string representation of the Role object.
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
    __tablename__ = 'department'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Department details
    department_name: so.Mapped[str] = so.mapped_column(sa.String(20), index=True, unique=True)

    # Relationship to User 
    users: so.Mapped[List['User']] = so.relationship('User', back_populates='department')
    
    def __repr__(self):
        """
        Returns a string representation of the Department object.
        """
        return f'<Department {self.department_name}>'
    

class TrainingModule (db.Model):    
    """
    Represents a training module in the system.

    Attributes:
        id (int): The unique identifier for the training module (primary key).
        module_title (str): The title of the training module.
        module_description (str): A detailed description of the training module.
        module_instructions (str): Instructions for completing the module.
        video_url (str): A URL to an instructional video for the module.
        questions (list[Question]): List of questions associated with the module.
        user_progress (list[UserModuleProgress]): List of user progress entries for this module.
        active (bool): Indicates whether the module is currently active.
    """ 
    __tablename__ = 'training_module'   

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Training module details
    module_title: so.Mapped[str] = so.mapped_column(sa.String(150), index=True, unique=True)
    module_description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    module_instructions: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    video_url: so.Mapped[str] = so.mapped_column(sa.String(300), nullable=True)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=True)

    # Relationship with questions   
    questions: so.Mapped[List['Question']] = so.relationship('Question', back_populates='training_module', cascade='all, delete-orphan')

    # Relationship with user progress
    user_progress: so.Mapped[List['UserModuleProgress']] = so.relationship('UserModuleProgress', back_populates='training_module')

    # Relationship with onboarding steps
    onboarding_steps: so.Mapped[List['OnboardingStep']] = so.relationship('OnboardingStep', back_populates='training_module', cascade='all, delete-orphan')

    def __repr__(self):
        """
        Returns a string representation of the TrainingModule object.
        """
        return f'<TrainingModule {self.module_title}>'


class Question (db.Model):
    """
    Represents a question in the system.

    Attributes:
        id (int): The unique identifier for the question (primary key).
        question_text (str): The text of the question.
        training_module_id (int): Foreign key to the associated training module.
        training_module (TrainingModule): The associated training module (relationship).
        options (list[Option]): List of answer options for the question.
    """
    __tablename__ = 'question'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Question details
    question_text: so.Mapped[str] = so.mapped_column(sa.String(1000), nullable=False)
    
    # Relationship with training module id
    training_module_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('training_module.id'), nullable=False)
    training_module: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='questions')

    # Relationship with options
    options: so.Mapped[List['Option']] = so.relationship('Option', back_populates='question', cascade='all, delete-orphan')

    def __repr__(self):
        """
        Returns a string representation of the Question object.
        """
        return f'<Question {self.question_text}>'


class Option (db.Model):
    """
    Represents an answer option for a question.

    Attributes:
        id (int): The unique identifier for the option (primary key).
        question_id (int): Foreign key to the associated question.
        option_text (str): The text of the option.
        is_correct (bool): Indicates whether the option is correct.
        question (Question): The associated question (relationship).
    """
    __tablename__ = "option"

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Option details
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('question.id'), nullable=False)
    option_text: so.Mapped[str] = so.mapped_column(sa.String(500), nullable=False)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)

    # Relationship with question
    question: so.Mapped['Question'] = so.relationship('Question', back_populates='options')

    def __repr__(self):
        """
        Returns a string representation of the Option object.
        """
        return f'<Option {self.option_text}>'


class UserModuleProgress (db.Model):
    """
    Represents the progress of a user in a training module.

    Attributes:
        id (int): Unique identifier for the progress entry.
        start_date (datetime): Date and time when the module was started.
        completed_date (datetime, optional): Date and time when the module was completed.
        score (int, optional): The score achieved by the user in the module.
        attempts (int): Number of attempts made by the user.
        user_id (int): Foreign key referencing the User model.
        user (User): The user associated with this progress entry (relationship).
        training_module_id (int): Foreign key referencing the TrainingModule model.
        training_module (TrainingModule): The training module associated with this progress entry (relationship).
        answers (list[UserQuestionAnswer]): List of answers associated with this progress entry.
    """
    __tablename__ = 'user_module_progress'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True) 

    # User Module Progress details
    start_date: so.Mapped[datetime] = so.mapped_column(
    sa.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=True)
    score: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    attempts: so.Mapped[int] = so.mapped_column(sa.Integer, default=0, nullable=False)

    # Relationship to User
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    user: so.Mapped['User'] = so.relationship('User', back_populates='module_progress')
    
     # Relationship to Training Module
    training_module_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('training_module.id'), nullable=False)
    training_module: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='user_progress')
    
    # Relationship to User Question Answer
    answers: so.Mapped[List['UserQuestionAnswer']] = so.relationship('UserQuestionAnswer', back_populates='progress', cascade='all, delete-orphan')


class UserQuestionAnswer (db.Model):
    """
    Represents an answer submitted by a user to a question.

    Attributes:
        id (int): Unique identifier for the answer entry.
        is_correct (bool): Indicates whether the answer is correct.
        progress_id (int): Foreign key referencing the UserModuleProgress model.
        progress (UserModuleProgress): The progress entry associated with this answer (relationship).
        question_id (int): Foreign key referencing the Question model.
        question (Question): The question associated with this answer (relationship).
        selected_option_id (int, optional): Foreign key referencing the Option model.
        selected_option (Option, optional): The selected option for this answer (relationship).
    """
    __tablename__ = 'user_question_answer'
    
    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    is_correct: so.Mapped[bool] = so.mapped_column(sa.Boolean)
    
    # User Question Answer details
    progress_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user_module_progress.id'), nullable=False)

    # Relationship to User Module Progress
    progress: so.Mapped['UserModuleProgress'] = so.relationship('UserModuleProgress', back_populates='answers')

    # Relationship to question
    question_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('question.id'), nullable=False)
    question: so.Mapped['Question'] = so.relationship('Question')
    
    # Relationship to option
    selected_option_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('option.id'), nullable=True)
    selected_option: so.Mapped['Option'] = so.relationship('Option')


class OnboardingPath(db.Model):
    """
    Represents an onboarding path for a staff type (e.g., office, operational).

    Attributes:
        id (int): Unique identifier for the onboarding path.
        path_name (str): The name of the onboarding path.
        steps (list[OnboardingStep]): List of steps in this onboarding path.
    """
    __tablename__ = 'onboarding_path'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    #Onboarding path details
    path_name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False, unique=True)

    # Relationship with onboarding steps
    steps: so.Mapped[List['OnboardingStep']] = so.relationship('OnboardingStep', back_populates='path', cascade='all, delete-orphan')

    def __repr__(self):
        """
        Returns a string representation of the Onboarding Path object.
        """
        return f"<OnboardingPath {self.path_name}>"
    

class OnboardingStep(db.Model):
    """
    Represents a single step in an onboarding path, such as a training module.
    
    Attributes:
        id (int): Unique identifier for the onboarding step.
        step_name (str): The name of the step.
        onboarding_path_id (int): Foreign key referencing the OnboardingPath model.
        path (OnboardingPath): The onboarding path associated with this step (relationship).
        training_module_id (int, optional): Foreign key referencing the TrainingModule model.
        training_module (TrainingModule, optional): The training module associated with this step (relationship).
    """
    __tablename__ = 'onboarding_step'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Onboarding Step details
    step_name: so.Mapped[str] = so.mapped_column(sa.String(150), nullable=False)
    
    # Relationship to Onboarding Path
    onboarding_path_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('onboarding_path.id'), nullable=False)
    path: so.Mapped['OnboardingPath'] = so.relationship('OnboardingPath', back_populates='steps')

    # Relationship to training modules
    training_module_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('training_module.id'), nullable=True)
    training_module: so.Mapped['TrainingModule'] = so.relationship('TrainingModule', back_populates='onboarding_steps')

    def __repr__(self):
        """
        Returns a string representation of the OnboardingStep object.
        """
        return f"<OnboardingStep {self.step_name}>"
    

class DocumentRepository(db.Model):
    """
    Represents a document in the repository.

    Attributes:
        id (int): Unique identifier for the document.
        document_title (str): The title of the document.
        document_category (str): The category of the document (e.g., Policy, Guide, Form).
        upload_date (datetime): The date and time the document was uploaded.
        file_path (str): The path to the uploaded file.
        user_id (int): Foreign key referencing the User model.
        uploaded_by_user (User): The user who uploaded the document (relationship).
    """
    __tablename__ = 'document_repository'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Repository details
    document_title: so.Mapped[str] = so.mapped_column(sa.String(150), nullable=False)
    document_category: so.Mapped[str] = so.mapped_column(sa.Enum('Policy', 'Guide', 'Form', name='document_category'), nullable=False)
    upload_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    file_path: so.Mapped[str] = so.mapped_column(sa.String(300), nullable=False)

    # Relationship to User
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)    
    uploaded_by_user: so.Mapped['User'] = so.relationship('User')

    def __repr__(self):
        """
        Returns a string representation of the Document Repository object.
        """
        return f"<DocumentRepository {self.document_title}>"

    
class Report(db.Model):
    """
    Represents a report in the system.
    
    Attributes:
        id (int): Unique identifier for the report.
        report_type (str): Type of report (e.g., Completion, Performance).
        description (str): Short description of the report.
        report_data (str, optional): Stored Json report content.
        created_at (datetime): Timestamp when the report was created.
    """
    __tablename__ = 'report'

    # Primary key
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Report details
    report_type: so.Mapped[str] = so.mapped_column(sa.Enum('Completion', 'Performance', name='report_type'), nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)    
    report_data: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)  
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Report object.
        """
        return f"<Report {self.report_type} created on {self.created_at}>"