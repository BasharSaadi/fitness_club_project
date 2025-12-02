from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class RegistrationStatus(enum.Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ClassRegistration(Base):
    """
    ClassRegistration entity - represents a member's registration for a class.
    
    Attributes:
        registration_id: Primary key
        member_id: Foreign key to Member
        class_id: Foreign key to FitnessClass
        status: Registration status
        registered_at: When the registration was made
    """
    __tablename__ = 'class_registrations'

    registration_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey('fitness_classes.class_id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.REGISTERED)
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="class_registrations")
    fitness_class = relationship("FitnessClass", back_populates="registrations")

    # Prevent duplicate registrations
    __table_args__ = (
        UniqueConstraint('member_id', 'class_id', name='uq_member_class_registration'),
    )

    def __repr__(self):
        return f"<ClassRegistration(id={self.registration_id}, member_id={self.member_id}, class_id={self.class_id})>"

    def to_dict(self):
        """Convert registration to dictionary representation."""
        return {
            'registration_id': self.registration_id,
            'member_id': self.member_id,
            'class_id': self.class_id,
            'status': self.status.value,
            'registered_at': str(self.registered_at)
        }
