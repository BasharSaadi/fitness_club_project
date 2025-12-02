from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class ClassStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FitnessClass(Base):
    """
    FitnessClass entity - represents a group fitness class.
    
    Attributes:
        class_id: Primary key
        name: Class name (e.g., "Morning Yoga", "HIIT Training")
        description: Detailed description of the class
        trainer_id: Foreign key to assigned Trainer
        room_id: Foreign key to assigned Room
        scheduled_time: Date and time of the class
        duration_minutes: Length of the class in minutes
        capacity: Maximum number of participants
        status: Current status of the class
    """
    __tablename__ = 'fitness_classes'

    class_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    trainer_id = Column(Integer, ForeignKey('trainers.trainer_id'), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(ClassStatus), default=ClassStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trainer = relationship("Trainer", back_populates="fitness_classes")
    room = relationship("Room", back_populates="fitness_classes")
    registrations = relationship("ClassRegistration", back_populates="fitness_class", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FitnessClass(id={self.class_id}, name='{self.name}', scheduled='{self.scheduled_time}')>"

    def to_dict(self):
        """Convert fitness class to dictionary representation."""
        return {
            'class_id': self.class_id,
            'name': self.name,
            'description': self.description,
            'trainer_id': self.trainer_id,
            'room_id': self.room_id,
            'scheduled_time': str(self.scheduled_time),
            'duration_minutes': self.duration_minutes,
            'capacity': self.capacity,
            'status': self.status.value,
            'created_at': str(self.created_at)
        }

    def get_end_time(self):
        """Calculate the end time of the class."""
        from datetime import timedelta
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)

    def current_registration_count(self):
        """Get the current number of registered members."""
        return len(self.registrations) if self.registrations else 0

    def has_capacity(self):
        """Check if the class has available spots."""
        return self.current_registration_count() < self.capacity
