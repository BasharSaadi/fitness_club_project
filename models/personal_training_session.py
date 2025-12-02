from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class SessionStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PersonalTrainingSession(Base):
    """
    PersonalTrainingSession entity - represents a personal training session.

    Attributes:
        session_id: Primary key
        member_id: Foreign key to Member
        trainer_id: Foreign key to Trainer
        room_id: Foreign key to Room (optional)
        scheduled_time: Date and time of the session
        duration_minutes: Length of the session in minutes
        notes: Optional session notes or goals
        status: Current status of the session
        created_at: When the session was booked
    """
    __tablename__ = 'personal_training_sessions'

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False, index=True)
    trainer_id = Column(Integer, ForeignKey('trainers.trainer_id', ondelete='CASCADE'), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=True, index=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    notes = Column(Text, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="personal_training_sessions")
    trainer = relationship("Trainer", back_populates="personal_training_sessions")
    room = relationship("Room", back_populates="personal_training_sessions")

    def __repr__(self):
        return f"<PersonalTrainingSession(id={self.session_id}, member_id={self.member_id}, trainer_id={self.trainer_id}, scheduled='{self.scheduled_time}')>"

    def to_dict(self):
        """Convert session to dictionary representation."""
        return {
            'session_id': self.session_id,
            'member_id': self.member_id,
            'trainer_id': self.trainer_id,
            'room_id': self.room_id,
            'scheduled_time': str(self.scheduled_time),
            'duration_minutes': self.duration_minutes,
            'notes': self.notes,
            'status': self.status.value,
            'created_at': str(self.created_at)
        }

    def get_end_time(self):
        """Calculate the end time of the session."""
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)
