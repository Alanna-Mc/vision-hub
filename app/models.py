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
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    surname: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # Foreign key to Role model
    role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('role.id'))

    # Relationship to Role model
    role: so.Mapped['Role'] = so.relationship('Role', back_populates='users')

    dateStarted: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    
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