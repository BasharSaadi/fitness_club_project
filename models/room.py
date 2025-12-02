from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class RoomType(enum.Enum):
    STUDIO = "studio"
    GYM_FLOOR = "gym_floor"
    TRAINING_ROOM = "training_room"
    POOL = "pool"
    OUTDOOR = "outdoor"


class Room(Base):
    """
    Room entity - represents a physical space in the fitness club.
    
    Attributes:
        room_id: Primary key
        name: Room name (e.g., "Studio A", "Main Gym Floor")
        capacity: Maximum number of people the room can hold
        room_type: Type of room (studio, gym floor, etc.)
    """
    __tablename__ = 'rooms'

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)

    # Relationships
    room_bookings = relationship("RoomBooking", back_populates="room", cascade="all, delete-orphan")
    fitness_classes = relationship("FitnessClass", back_populates="room")
    personal_training_sessions = relationship("PersonalTrainingSession", back_populates="room")

    def __repr__(self):
        return f"<Room(id={self.room_id}, name='{self.name}', capacity={self.capacity})>"

    def to_dict(self):
        """Convert room to dictionary representation."""
        return {
            'room_id': self.room_id,
            'name': self.name,
            'capacity': self.capacity,
            'room_type': self.room_type.value
        }
