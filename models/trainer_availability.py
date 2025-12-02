from sqlalchemy import Column, Integer, Time, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class DayOfWeek(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class TrainerAvailability(Base):
    """
    TrainerAvailability entity - represents a trainer's available time slot.
    
    Trainers can define recurring weekly availability slots.
    The system prevents overlapping time slots for the same trainer.
    
    Attributes:
        availability_id: Primary key
        trainer_id: Foreign key to Trainer
        day_of_week: Day of the week (0=Monday, 6=Sunday)
        start_time: Start time of availability
        end_time: End time of availability
    """
    __tablename__ = 'trainer_availability'

    availability_id = Column(Integer, primary_key=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey('trainers.trainer_id', ondelete='CASCADE'), nullable=False, index=True)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationships
    trainer = relationship("Trainer", back_populates="availability_slots")

    # Ensure no exact duplicate slots
    __table_args__ = (
        UniqueConstraint('trainer_id', 'day_of_week', 'start_time', 'end_time', name='uq_trainer_availability_slot'),
    )

    def __repr__(self):
        return f"<TrainerAvailability(id={self.availability_id}, trainer_id={self.trainer_id}, day={self.day_of_week.name}, {self.start_time}-{self.end_time})>"

    def to_dict(self):
        """Convert availability to dictionary representation."""
        return {
            'availability_id': self.availability_id,
            'trainer_id': self.trainer_id,
            'day_of_week': self.day_of_week.name,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time)
        }

    def overlaps_with(self, other):
        """Check if this availability slot overlaps with another slot."""
        if self.trainer_id != other.trainer_id:
            return False
        if self.day_of_week != other.day_of_week:
            return False
        # Check time overlap: slots overlap if one starts before the other ends
        return (self.start_time < other.end_time) and (other.start_time < self.end_time)
