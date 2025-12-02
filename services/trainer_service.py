import hashlib
import re
from datetime import time, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Trainer, TrainerAvailability, DayOfWeek, FitnessClass


class TrainerService:
    """Service class for trainer operations."""

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

    def register_trainer(self, email: str, password: str, first_name: str, last_name: str,
                         specialization: str = None, phone: str = None) -> dict:
        """
        Register a new trainer.
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        if not self.validate_email(email):
            return {'success': False, 'error': 'Invalid email format'}
        
        if len(password) < 8:
            return {'success': False, 'error': 'Password must be at least 8 characters'}
        
        if not first_name or not last_name:
            return {'success': False, 'error': 'First name and last name are required'}

        existing = self.session.query(Trainer).filter(Trainer.email == email.lower()).first()
        if existing:
            return {'success': False, 'error': 'Email already registered'}

        try:
            trainer = Trainer(
                email=email.lower(),
                password_hash=self.hash_password(password),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                specialization=specialization,
                phone=phone
            )
            self.session.add(trainer)
            self.session.commit()
            return {'success': True, 'data': trainer.to_dict()}
        except IntegrityError:
            self.session.rollback()
            return {'success': False, 'error': 'Database error'}

    def authenticate_trainer(self, email: str, password: str) -> dict:
        """
        Authenticate a trainer.
        
        Returns:
            dict with 'success' boolean and 'data' (trainer) or 'error' message
        """
        trainer = self.session.query(Trainer).filter(Trainer.email == email.lower()).first()
        if not trainer:
            return {'success': False, 'error': 'Invalid email or password'}
        
        if trainer.password_hash != self.hash_password(password):
            return {'success': False, 'error': 'Invalid email or password'}
        
        return {'success': True, 'data': trainer}

    def get_trainer_by_id(self, trainer_id: int) -> Trainer:
        """Get a trainer by ID."""
        return self.session.query(Trainer).filter(Trainer.trainer_id == trainer_id).first()

    def get_all_trainers(self) -> list:
        """Get all trainers."""
        return self.session.query(Trainer).all()

    def set_availability(self, trainer_id: int, day_of_week: str, 
                         start_time: time, end_time: time) -> dict:
        """
        Set trainer availability for a specific day and time.
        Prevents overlapping time slots for the same trainer.
        
        Args:
            trainer_id: Trainer's ID
            day_of_week: Day name (e.g., 'monday', 'tuesday')
            start_time: Start time of availability
            end_time: End time of availability
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        trainer = self.get_trainer_by_id(trainer_id)
        if not trainer:
            return {'success': False, 'error': 'Trainer not found'}

        # Parse day of week
        try:
            day_enum = DayOfWeek[day_of_week.upper()]
        except KeyError:
            return {'success': False, 'error': f'Invalid day. Must be one of: {[d.name for d in DayOfWeek]}'}

        # Validate times
        if start_time >= end_time:
            return {'success': False, 'error': 'End time must be after start time'}

        # Check for overlapping slots
        existing_slots = (self.session.query(TrainerAvailability)
                         .filter(TrainerAvailability.trainer_id == trainer_id)
                         .filter(TrainerAvailability.day_of_week == day_enum)
                         .all())

        new_slot = TrainerAvailability(
            trainer_id=trainer_id,
            day_of_week=day_enum,
            start_time=start_time,
            end_time=end_time
        )

        for slot in existing_slots:
            if new_slot.overlaps_with(slot):
                return {
                    'success': False, 
                    'error': f'Time slot overlaps with existing availability ({slot.start_time}-{slot.end_time})'
                }

        try:
            self.session.add(new_slot)
            self.session.commit()
            return {'success': True, 'data': new_slot.to_dict()}
        except IntegrityError:
            self.session.rollback()
            return {'success': False, 'error': 'This exact time slot already exists'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_availability(self, trainer_id: int) -> list:
        """Get all availability slots for a trainer."""
        return (self.session.query(TrainerAvailability)
                .filter(TrainerAvailability.trainer_id == trainer_id)
                .order_by(TrainerAvailability.day_of_week, TrainerAvailability.start_time)
                .all())

    def delete_availability(self, trainer_id: int, availability_id: int) -> dict:
        """Delete an availability slot."""
        slot = (self.session.query(TrainerAvailability)
                .filter(TrainerAvailability.availability_id == availability_id)
                .filter(TrainerAvailability.trainer_id == trainer_id)
                .first())
        
        if not slot:
            return {'success': False, 'error': 'Availability slot not found'}

        try:
            self.session.delete(slot)
            self.session.commit()
            return {'success': True, 'data': 'Availability slot deleted'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_schedule(self, trainer_id: int) -> dict:
        """
        Get trainer's schedule including availability and assigned classes.
        
        Returns:
            dict with availability slots and assigned classes
        """
        trainer = self.get_trainer_by_id(trainer_id)
        if not trainer:
            return {'success': False, 'error': 'Trainer not found'}

        availability = self.get_availability(trainer_id)
        
        # Get upcoming classes assigned to this trainer
        upcoming_classes = (self.session.query(FitnessClass)
                          .filter(FitnessClass.trainer_id == trainer_id)
                          .filter(FitnessClass.scheduled_time >= datetime.now())
                          .order_by(FitnessClass.scheduled_time)
                          .all())

        return {
            'success': True,
            'data': {
                'trainer': trainer.to_dict(),
                'availability': [slot.to_dict() for slot in availability],
                'upcoming_classes': [cls.to_dict() for cls in upcoming_classes]
            }
        }

    def is_available_at(self, trainer_id: int, day_of_week: DayOfWeek, 
                        check_time: time) -> bool:
        """Check if trainer is available at a specific day and time."""
        slots = (self.session.query(TrainerAvailability)
                .filter(TrainerAvailability.trainer_id == trainer_id)
                .filter(TrainerAvailability.day_of_week == day_of_week)
                .all())
        
        for slot in slots:
            if slot.start_time <= check_time < slot.end_time:
                return True
        return False
