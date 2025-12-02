import hashlib
import re
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import (Admin, Room, RoomType, RoomBooking, BookingStatus,
                    FitnessClass, ClassStatus, Trainer)


class AdminService:
    """Service class for administrative operations."""

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def register_admin(self, email: str, password: str, first_name: str, last_name: str) -> dict:
        """Register a new admin."""
        if not self.validate_email(email):
            return {'success': False, 'error': 'Invalid email format'}
        
        if len(password) < 8:
            return {'success': False, 'error': 'Password must be at least 8 characters'}

        existing = self.session.query(Admin).filter(Admin.email == email.lower()).first()
        if existing:
            return {'success': False, 'error': 'Email already registered'}

        try:
            admin = Admin(
                email=email.lower(),
                password_hash=self.hash_password(password),
                first_name=first_name.strip(),
                last_name=last_name.strip()
            )
            self.session.add(admin)
            self.session.commit()
            return {'success': True, 'data': admin.to_dict()}
        except IntegrityError:
            self.session.rollback()
            return {'success': False, 'error': 'Database error'}

    def authenticate_admin(self, email: str, password: str) -> dict:
        """Authenticate an admin."""
        admin = self.session.query(Admin).filter(Admin.email == email.lower()).first()
        if not admin:
            return {'success': False, 'error': 'Invalid email or password'}
        
        if admin.password_hash != self.hash_password(password):
            return {'success': False, 'error': 'Invalid email or password'}
        
        return {'success': True, 'data': admin}

    def get_admin_by_id(self, admin_id: int) -> Admin:
        """Get an admin by ID."""
        return self.session.query(Admin).filter(Admin.admin_id == admin_id).first()

    # ==================== Room Management ====================

    def create_room(self, name: str, capacity: int, room_type: str) -> dict:
        """Create a new room."""
        if capacity <= 0:
            return {'success': False, 'error': 'Capacity must be positive'}

        try:
            room_type_enum = RoomType(room_type.lower())
        except ValueError:
            return {'success': False, 'error': f'Invalid room type. Must be one of: {[r.value for r in RoomType]}'}

        existing = self.session.query(Room).filter(Room.name == name).first()
        if existing:
            return {'success': False, 'error': 'Room with this name already exists'}

        try:
            room = Room(
                name=name,
                capacity=capacity,
                room_type=room_type_enum
            )
            self.session.add(room)
            self.session.commit()
            return {'success': True, 'data': room.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_room_by_id(self, room_id: int) -> Room:
        """Get a room by ID."""
        return self.session.query(Room).filter(Room.room_id == room_id).first()

    def get_all_rooms(self) -> list:
        """Get all rooms."""
        return self.session.query(Room).all()

    def book_room(self, room_id: int, booking_date: date, start_time: time, 
                  end_time: time, purpose: str = None, admin_id: int = None) -> dict:
        """
        Book a room for a specific date and time.
        Prevents double-booking.
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        room = self.get_room_by_id(room_id)
        if not room:
            return {'success': False, 'error': 'Room not found'}

        if start_time >= end_time:
            return {'success': False, 'error': 'End time must be after start time'}

        if booking_date < date.today():
            return {'success': False, 'error': 'Cannot book for past dates'}

        # Check for conflicting bookings
        new_booking = RoomBooking(
            room_id=room_id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            purpose=purpose,
            booked_by_admin_id=admin_id
        )

        existing_bookings = (self.session.query(RoomBooking)
                           .filter(RoomBooking.room_id == room_id)
                           .filter(RoomBooking.booking_date == booking_date)
                           .filter(RoomBooking.status != BookingStatus.CANCELLED)
                           .all())

        for booking in existing_bookings:
            if new_booking.conflicts_with(booking):
                return {
                    'success': False,
                    'error': f'Room is already booked from {booking.start_time} to {booking.end_time}'
                }

        try:
            self.session.add(new_booking)
            self.session.commit()
            return {'success': True, 'data': new_booking.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_room_bookings(self, room_id: int, from_date: date = None) -> list:
        """Get bookings for a room, optionally from a specific date."""
        query = (self.session.query(RoomBooking)
                .filter(RoomBooking.room_id == room_id)
                .filter(RoomBooking.status != BookingStatus.CANCELLED))
        
        if from_date:
            query = query.filter(RoomBooking.booking_date >= from_date)
        
        return query.order_by(RoomBooking.booking_date, RoomBooking.start_time).all()

    def cancel_room_booking(self, booking_id: int) -> dict:
        """Cancel a room booking."""
        booking = self.session.query(RoomBooking).filter(RoomBooking.booking_id == booking_id).first()
        if not booking:
            return {'success': False, 'error': 'Booking not found'}

        booking.status = BookingStatus.CANCELLED
        try:
            self.session.commit()
            return {'success': True, 'data': 'Booking cancelled'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def is_room_available(self, room_id: int, booking_date: date, 
                          start_time: time, end_time: time) -> bool:
        """Check if a room is available for a specific date and time."""
        existing_bookings = (self.session.query(RoomBooking)
                           .filter(RoomBooking.room_id == room_id)
                           .filter(RoomBooking.booking_date == booking_date)
                           .filter(RoomBooking.status != BookingStatus.CANCELLED)
                           .all())

        for booking in existing_bookings:
            # Check time overlap
            if (start_time < booking.end_time) and (booking.start_time < end_time):
                return False
        return True

    # ==================== Class Management ====================

    def create_class(self, name: str, trainer_id: int, room_id: int, 
                     scheduled_time: datetime, duration_minutes: int = 60,
                     capacity: int = None, description: str = None) -> dict:
        """
        Create a new fitness class.
        
        Validates:
        - Trainer exists
        - Room exists
        - Class capacity doesn't exceed room capacity
        - No scheduling conflicts
        """
        # Validate trainer
        trainer = self.session.query(Trainer).filter(Trainer.trainer_id == trainer_id).first()
        if not trainer:
            return {'success': False, 'error': 'Trainer not found'}

        # Validate room
        room = self.get_room_by_id(room_id)
        if not room:
            return {'success': False, 'error': 'Room not found'}

        # Set capacity
        if capacity is None:
            capacity = room.capacity
        elif capacity > room.capacity:
            return {'success': False, 'error': f'Class capacity ({capacity}) exceeds room capacity ({room.capacity})'}

        if duration_minutes <= 0:
            return {'success': False, 'error': 'Duration must be positive'}

        if scheduled_time < datetime.now():
            return {'success': False, 'error': 'Cannot schedule class in the past'}

        # Calculate end time
        end_time = scheduled_time + timedelta(minutes=duration_minutes)
        booking_date = scheduled_time.date()
        start_time_only = scheduled_time.time()
        end_time_only = end_time.time()

        # Check room availability
        if not self.is_room_available(room_id, booking_date, start_time_only, end_time_only):
            return {'success': False, 'error': 'Room is not available at this time'}

        try:
            fitness_class = FitnessClass(
                name=name,
                description=description,
                trainer_id=trainer_id,
                room_id=room_id,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                capacity=capacity,
                status=ClassStatus.SCHEDULED
            )
            self.session.add(fitness_class)

            # Also book the room
            room_booking = RoomBooking(
                room_id=room_id,
                booking_date=booking_date,
                start_time=start_time_only,
                end_time=end_time_only,
                purpose=f'Fitness Class: {name}',
                status=BookingStatus.CONFIRMED
            )
            self.session.add(room_booking)

            self.session.commit()
            return {'success': True, 'data': fitness_class.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_class_by_id(self, class_id: int) -> FitnessClass:
        """Get a class by ID."""
        return self.session.query(FitnessClass).filter(FitnessClass.class_id == class_id).first()

    def get_all_classes(self, include_past: bool = False) -> list:
        """Get all fitness classes."""
        query = self.session.query(FitnessClass)
        if not include_past:
            query = query.filter(FitnessClass.scheduled_time >= datetime.now())
        return query.order_by(FitnessClass.scheduled_time).all()

    def update_class(self, class_id: int, **kwargs) -> dict:
        """
        Update a fitness class.
        
        Allowed fields: name, description, scheduled_time, duration_minutes, capacity, status
        """
        fitness_class = self.get_class_by_id(class_id)
        if not fitness_class:
            return {'success': False, 'error': 'Class not found'}

        allowed_fields = ['name', 'description', 'scheduled_time', 'duration_minutes', 'capacity', 'status']
        
        for field, value in kwargs.items():
            if field not in allowed_fields:
                continue
            
            if field == 'status' and value:
                try:
                    value = ClassStatus(value.lower())
                except ValueError:
                    return {'success': False, 'error': 'Invalid status value'}
            
            if field == 'capacity' and value:
                room = fitness_class.room
                if value > room.capacity:
                    return {'success': False, 'error': f'Capacity cannot exceed room capacity ({room.capacity})'}
            
            setattr(fitness_class, field, value)

        try:
            self.session.commit()
            return {'success': True, 'data': fitness_class.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def cancel_class(self, class_id: int) -> dict:
        """Cancel a fitness class."""
        fitness_class = self.get_class_by_id(class_id)
        if not fitness_class:
            return {'success': False, 'error': 'Class not found'}

        fitness_class.status = ClassStatus.CANCELLED
        try:
            self.session.commit()
            return {'success': True, 'data': 'Class cancelled'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_upcoming_classes(self) -> list:
        """Get all upcoming classes."""
        return (self.session.query(FitnessClass)
                .filter(FitnessClass.scheduled_time >= datetime.now())
                .filter(FitnessClass.status == ClassStatus.SCHEDULED)
                .order_by(FitnessClass.scheduled_time)
                .all())
