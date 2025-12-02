from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Member(Base):
    """
    Member entity - represents a gym member.
    
    Attributes:
        member_id: Primary key
        email: Unique email address for login
        password_hash: Hashed password for authentication
        first_name: Member's first name
        last_name: Member's last name
        date_of_birth: Member's date of birth
        gender: Member's gender
        phone: Contact phone number
        created_at: Account creation timestamp
    """
    __tablename__ = 'members'

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    health_metrics = relationship("HealthMetric", back_populates="member", cascade="all, delete-orphan")
    fitness_goals = relationship("FitnessGoal", back_populates="member", cascade="all, delete-orphan")
    class_registrations = relationship("ClassRegistration", back_populates="member", cascade="all, delete-orphan")
    personal_training_sessions = relationship("PersonalTrainingSession", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.member_id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"

    def to_dict(self):
        """Convert member to dictionary representation."""
        return {
            'member_id': self.member_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': str(self.date_of_birth) if self.date_of_birth else None,
            'gender': self.gender.value if self.gender else None,
            'phone': self.phone,
            'created_at': str(self.created_at)
        }
