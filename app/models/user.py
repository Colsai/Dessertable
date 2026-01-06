"""
User model for authentication
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


@dataclass
class User:
    """User data model for authentication"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    created_at: Optional[datetime] = None

    def set_password(self, password: str):
        """Hash and set user password using scrypt"""
        self.password_hash = generate_password_hash(
            password,
            method='scrypt'  # Modern, secure hashing (Flask 3.0+)
        )

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    # Flask-Login integration properties
    @property
    def is_authenticated(self) -> bool:
        """Required by Flask-Login"""
        return True

    @property
    def is_active(self) -> bool:
        """Required by Flask-Login"""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Required by Flask-Login"""
        return False

    def get_id(self) -> str:
        """
        Required by Flask-Login
        Returns unique identifier as string
        """
        return str(self.id)
