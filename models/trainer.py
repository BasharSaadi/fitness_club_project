from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from models.base import Base


class Trainer(Base):
    """
    Trainer entity - represents a fitness trainer.
    
    Attributes:
        trainer_id: Primary key
        email: Unique email address for login
        password_hash: Hashed password for authentication
        first_name: Trainer's first name
        last_name: Trainer's last name
        specialization: Areas of expertise (e.g., "Yoga, Strength Training")
        phone: Contact phone number
        created_at: Account creation timestamp
    """
    __tablename__ = 'trainers'

    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    availability_slots = relationship("TrainerAvailability", back_populates="trainer", cascade="all, delete-orphan")
    fitness_classes = relationship("FitnessClass", back_populates="trainer")
    personal_training_sessions = relationship("PersonalTrainingSession", back_populates="trainer")

    def __repr__(self):
        return f"<Trainer(id={self.trainer_id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"

    def to_dict(self):
        """Convert trainer to dictionary representation."""
        return {
            'trainer_id': self.trainer_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'specialization': self.specialization,
            'phone': self.phone,
            'created_at': str(self.created_at)
        }
