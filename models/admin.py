from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base


class Admin(Base):
    """
    Admin entity - represents an administrative staff member.
    
    Attributes:
        admin_id: Primary key
        email: Unique email address for login
        password_hash: Hashed password for authentication
        first_name: Admin's first name
        last_name: Admin's last name
        created_at: Account creation timestamp
    """
    __tablename__ = 'admins'

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Admin(id={self.admin_id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"

    def to_dict(self):
        """Convert admin to dictionary representation."""
        return {
            'admin_id': self.admin_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': str(self.created_at)
        }
