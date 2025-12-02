from datetime import datetime
from sqlalchemy import Column, Integer, Date, Time, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class BookingStatus(enum.Enum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class RoomBooking(Base):
    """
    RoomBooking entity - represents a room reservation.
    
    Used to manage room allocations and prevent double-booking.
    
    Attributes:
        booking_id: Primary key
        room_id: Foreign key to Room
        booking_date: Date of the booking
        start_time: Start time of the booking
        end_time: End time of the booking
        purpose: Description of the booking purpose
        booked_by_admin_id: Admin who made the booking
        status: Current status of the booking
    """
    __tablename__ = 'room_bookings'

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.room_id', ondelete='CASCADE'), nullable=False, index=True)
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    purpose = Column(Text, nullable=True)
    booked_by_admin_id = Column(Integer, ForeignKey('admins.admin_id'), nullable=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="room_bookings")

    def __repr__(self):
        return f"<RoomBooking(id={self.booking_id}, room_id={self.room_id}, date='{self.booking_date}', {self.start_time}-{self.end_time})>"

    def to_dict(self):
        """Convert room booking to dictionary representation."""
        return {
            'booking_id': self.booking_id,
            'room_id': self.room_id,
            'booking_date': str(self.booking_date),
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'purpose': self.purpose,
            'booked_by_admin_id': self.booked_by_admin_id,
            'status': self.status.value,
            'created_at': str(self.created_at)
        }

    def conflicts_with(self, other):
        """Check if this booking conflicts with another booking for the same room."""
        if self.room_id != other.room_id:
            return False
        if self.booking_date != other.booking_date:
            return False
        if self.status == BookingStatus.CANCELLED or other.status == BookingStatus.CANCELLED:
            return False
        # Check time overlap
        return (self.start_time < other.end_time) and (other.start_time < self.end_time)
