import hashlib
import re
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from models import (Member, Gender, HealthMetric, FitnessGoal, GoalType, GoalStatus,
                    ClassRegistration, PersonalTrainingSession, SessionStatus,
                    FitnessClass, ClassStatus, RegistrationStatus, Trainer,
                    TrainerAvailability, DayOfWeek)


class MemberService:
    """Service class for member operations."""

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

    def register_member(self, email: str, password: str, first_name: str, last_name: str,
                        date_of_birth: date = None, gender: str = None, phone: str = None) -> dict:
        """
        Register a new member.
        
        Args:
            email: Unique email address
            password: Password (min 8 characters)
            first_name: Member's first name
            last_name: Member's last name
            date_of_birth: Optional date of birth
            gender: Optional gender (male/female/other/prefer_not_to_say)
            phone: Optional phone number
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        # Validation
        if not self.validate_email(email):
            return {'success': False, 'error': 'Invalid email format'}
        
        if len(password) < 8:
            return {'success': False, 'error': 'Password must be at least 8 characters'}
        
        if not first_name or not last_name:
            return {'success': False, 'error': 'First name and last name are required'}
        
        if date_of_birth and date_of_birth > date.today():
            return {'success': False, 'error': 'Date of birth cannot be in the future'}

        # Check for existing email
        existing = self.session.query(Member).filter(Member.email == email.lower()).first()
        if existing:
            return {'success': False, 'error': 'Email already registered'}

        # Parse gender
        gender_enum = None
        if gender:
            try:
                gender_enum = Gender(gender.lower())
            except ValueError:
                return {'success': False, 'error': f'Invalid gender. Must be one of: {[g.value for g in Gender]}'}

        # Create member
        try:
            member = Member(
                email=email.lower(),
                password_hash=self.hash_password(password),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                date_of_birth=date_of_birth,
                gender=gender_enum,
                phone=phone
            )
            self.session.add(member)
            self.session.commit()
            return {'success': True, 'data': member.to_dict()}
        except IntegrityError:
            self.session.rollback()
            return {'success': False, 'error': 'Database error: Email may already exist'}

    def authenticate_member(self, email: str, password: str) -> dict:
        """
        Authenticate a member.
        
        Returns:
            dict with 'success' boolean and 'data' (member) or 'error' message
        """
        member = self.session.query(Member).filter(Member.email == email.lower()).first()
        if not member:
            return {'success': False, 'error': 'Invalid email or password'}
        
        if member.password_hash != self.hash_password(password):
            return {'success': False, 'error': 'Invalid email or password'}
        
        return {'success': True, 'data': member}

    def get_member_by_id(self, member_id: int) -> Member:
        """Get a member by ID."""
        return self.session.query(Member).filter(Member.member_id == member_id).first()

    def update_profile(self, member_id: int, **kwargs) -> dict:
        """
        Update member profile.
        
        Allowed fields: first_name, last_name, phone, date_of_birth, gender
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        member = self.get_member_by_id(member_id)
        if not member:
            return {'success': False, 'error': 'Member not found'}

        allowed_fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'gender']
        
        for field, value in kwargs.items():
            if field not in allowed_fields:
                continue
            
            if field == 'gender' and value:
                try:
                    value = Gender(value.lower())
                except ValueError:
                    return {'success': False, 'error': f'Invalid gender value'}
            
            if field == 'date_of_birth' and value and value > date.today():
                return {'success': False, 'error': 'Date of birth cannot be in the future'}
            
            setattr(member, field, value)

        try:
            self.session.commit()
            return {'success': True, 'data': member.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def log_health_metric(self, member_id: int, weight_kg: float = None, height_cm: float = None,
                          heart_rate_bpm: int = None, body_fat_percentage: float = None) -> dict:
        """
        Log a new health metric entry. Does NOT overwrite previous entries.
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        member = self.get_member_by_id(member_id)
        if not member:
            return {'success': False, 'error': 'Member not found'}

        # Validation
        if weight_kg is not None and weight_kg <= 0:
            return {'success': False, 'error': 'Weight must be positive'}
        if height_cm is not None and height_cm <= 0:
            return {'success': False, 'error': 'Height must be positive'}
        if heart_rate_bpm is not None and heart_rate_bpm <= 0:
            return {'success': False, 'error': 'Heart rate must be positive'}
        if body_fat_percentage is not None and (body_fat_percentage < 0 or body_fat_percentage > 100):
            return {'success': False, 'error': 'Body fat percentage must be between 0 and 100'}

        # At least one metric must be provided
        if all(v is None for v in [weight_kg, height_cm, heart_rate_bpm, body_fat_percentage]):
            return {'success': False, 'error': 'At least one health metric must be provided'}

        try:
            metric = HealthMetric(
                member_id=member_id,
                weight_kg=weight_kg,
                height_cm=height_cm,
                heart_rate_bpm=heart_rate_bpm,
                body_fat_percentage=body_fat_percentage
            )
            self.session.add(metric)
            self.session.commit()
            return {'success': True, 'data': metric.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_health_history(self, member_id: int, limit: int = 10) -> list:
        """
        Get member's health metric history.
        
        Returns list of health metrics, most recent first.
        """
        return (self.session.query(HealthMetric)
                .filter(HealthMetric.member_id == member_id)
                .order_by(HealthMetric.recorded_at.desc())
                .limit(limit)
                .all())

    def get_latest_health_metric(self, member_id: int) -> HealthMetric:
        """Get the most recent health metric for a member."""
        return (self.session.query(HealthMetric)
                .filter(HealthMetric.member_id == member_id)
                .order_by(HealthMetric.recorded_at.desc())
                .first())

    def create_fitness_goal(self, member_id: int, goal_type: str, target_value: float,
                            current_value: float = None, deadline: date = None) -> dict:
        """
        Create a new fitness goal.
        
        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        member = self.get_member_by_id(member_id)
        if not member:
            return {'success': False, 'error': 'Member not found'}

        try:
            goal_type_enum = GoalType(goal_type.lower())
        except ValueError:
            return {'success': False, 'error': f'Invalid goal type. Must be one of: {[g.value for g in GoalType]}'}

        if target_value <= 0:
            return {'success': False, 'error': 'Target value must be positive'}

        if deadline and deadline < date.today():
            return {'success': False, 'error': 'Deadline cannot be in the past'}

        try:
            goal = FitnessGoal(
                member_id=member_id,
                goal_type=goal_type_enum,
                target_value=target_value,
                current_value=current_value,
                deadline=deadline,
                status=GoalStatus.ACTIVE
            )
            self.session.add(goal)
            self.session.commit()
            return {'success': True, 'data': goal.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_active_goals(self, member_id: int) -> list:
        """Get all active fitness goals for a member."""
        return (self.session.query(FitnessGoal)
                .filter(FitnessGoal.member_id == member_id)
                .filter(FitnessGoal.status == GoalStatus.ACTIVE)
                .all())

    def update_goal(self, goal_id: int, member_id: int, **kwargs) -> dict:
        """
        Update a fitness goal.
        
        Allowed fields: current_value, target_value, deadline, status
        """
        goal = (self.session.query(FitnessGoal)
                .filter(FitnessGoal.goal_id == goal_id)
                .filter(FitnessGoal.member_id == member_id)
                .first())
        
        if not goal:
            return {'success': False, 'error': 'Goal not found'}

        allowed_fields = ['current_value', 'target_value', 'deadline', 'status']
        
        for field, value in kwargs.items():
            if field not in allowed_fields:
                continue
            
            if field == 'status' and value:
                try:
                    value = GoalStatus(value.lower())
                except ValueError:
                    return {'success': False, 'error': 'Invalid status value'}
            
            setattr(goal, field, value)

        try:
            self.session.commit()
            return {'success': True, 'data': goal.to_dict()}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_dashboard_data(self, member_id: int) -> dict:
        """
        Get dashboard summary data for a member.
        
        Returns:
            dict containing:
            - member info
            - latest health metrics
            - active goals
            - past class count
            - upcoming sessions (placeholder)
        """
        member = self.get_member_by_id(member_id)
        if not member:
            return {'success': False, 'error': 'Member not found'}

        latest_metric = self.get_latest_health_metric(member_id)
        active_goals = self.get_active_goals(member_id)
        
        # Count past classes (attended)
        past_class_count = (self.session.query(ClassRegistration)
                          .filter(ClassRegistration.member_id == member_id)
                          .count())

        return {
            'success': True,
            'data': {
                'member': member.to_dict(),
                'latest_metric': latest_metric.to_dict() if latest_metric else None,
                'active_goals': [g.to_dict() for g in active_goals],
                'past_class_count': past_class_count,
                'health_history_count': len(member.health_metrics)
            }
        }

    def search_members(self, name_query: str) -> list:
        """
        Search members by name (case-insensitive partial match).
        Used by trainers for member lookup.
        """
        query = name_query.lower()
        return (self.session.query(Member)
                .filter(
                    (Member.first_name.ilike(f'%{query}%')) |
                    (Member.last_name.ilike(f'%{query}%'))
                )
                .all())

    # ==================== Personal Training Session Methods ====================

    def get_available_trainers(self) -> list:
        """Get all trainers."""
        return self.session.query(Trainer).all()

    def book_personal_training_session(self, member_id: int, trainer_id: int,
                                       scheduled_time: datetime, duration_minutes: int = 60,
                                       room_id: int = None, notes: str = None) -> dict:
        """
        Book a personal training session.

        Validates:
        - Trainer availability (day of week and time)
        - No time conflicts with existing sessions for trainer
        - No time conflicts with member's existing sessions
        - Room availability (if room specified)

        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        # Validate member exists
        member = self.get_member_by_id(member_id)
        if not member:
            return {'success': False, 'error': 'Member not found'}

        # Validate trainer exists
        trainer = self.session.query(Trainer).filter(Trainer.trainer_id == trainer_id).first()
        if not trainer:
            return {'success': False, 'error': 'Trainer not found'}

        # Validate scheduled time is in the future
        if scheduled_time <= datetime.now():
            return {'success': False, 'error': 'Session must be scheduled in the future'}

        # Calculate end time
        end_time = scheduled_time + timedelta(minutes=duration_minutes)

        # Check trainer availability (day of week and time)
        day_of_week = DayOfWeek[scheduled_time.strftime('%A').upper()]
        start_time = scheduled_time.time()

        trainer_available = (self.session.query(TrainerAvailability)
                           .filter(TrainerAvailability.trainer_id == trainer_id)
                           .filter(TrainerAvailability.day_of_week == day_of_week)
                           .filter(TrainerAvailability.start_time <= start_time)
                           .filter(TrainerAvailability.end_time >= end_time.time())
                           .first())

        if not trainer_available:
            return {
                'success': False,
                'error': f'Trainer is not available on {day_of_week.name.title()} at {start_time.strftime("%H:%M")}'
            }

        # Check for trainer conflicts (existing sessions)
        trainer_conflict = (self.session.query(PersonalTrainingSession)
                          .filter(PersonalTrainingSession.trainer_id == trainer_id)
                          .filter(PersonalTrainingSession.status == SessionStatus.SCHEDULED)
                          .filter(PersonalTrainingSession.scheduled_time < end_time)
                          .filter(PersonalTrainingSession.scheduled_time >= scheduled_time)
                          .first())

        if trainer_conflict:
            return {'success': False, 'error': 'Trainer has a conflicting session at this time'}

        # Check for member conflicts (existing sessions or classes)
        member_session_conflict = (self.session.query(PersonalTrainingSession)
                                 .filter(PersonalTrainingSession.member_id == member_id)
                                 .filter(PersonalTrainingSession.status == SessionStatus.SCHEDULED)
                                 .filter(PersonalTrainingSession.scheduled_time < end_time)
                                 .filter(PersonalTrainingSession.scheduled_time >= scheduled_time)
                                 .first())

        if member_session_conflict:
            return {'success': False, 'error': 'You have a conflicting session at this time'}

        # Check room availability if room is specified
        if room_id:
            from models import RoomBooking, BookingStatus
            room_conflict = (self.session.query(RoomBooking)
                           .filter(RoomBooking.room_id == room_id)
                           .filter(RoomBooking.booking_date == scheduled_time.date())
                           .filter(RoomBooking.status == BookingStatus.CONFIRMED)
                           .filter(
                               and_(
                                   RoomBooking.start_time < end_time.time(),
                                   RoomBooking.end_time > start_time
                               )
                           )
                           .first())

            if room_conflict:
                return {'success': False, 'error': 'Room is not available at this time'}

        # Create the session
        try:
            session = PersonalTrainingSession(
                member_id=member_id,
                trainer_id=trainer_id,
                room_id=room_id,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                notes=notes,
                status=SessionStatus.SCHEDULED
            )
            self.session.add(session)
            self.session.commit()
            return {'success': True, 'data': session.to_dict(), 'session_id': session.session_id}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_member_pt_sessions(self, member_id: int, upcoming_only: bool = True) -> list:
        """Get member's personal training sessions."""
        query = (self.session.query(PersonalTrainingSession)
                .filter(PersonalTrainingSession.member_id == member_id))

        if upcoming_only:
            query = query.filter(PersonalTrainingSession.scheduled_time >= datetime.now())
            query = query.filter(PersonalTrainingSession.status == SessionStatus.SCHEDULED)

        return query.order_by(PersonalTrainingSession.scheduled_time).all()

    def cancel_pt_session(self, member_id: int, session_id: int) -> dict:
        """Cancel a personal training session."""
        session = (self.session.query(PersonalTrainingSession)
                  .filter(PersonalTrainingSession.session_id == session_id)
                  .filter(PersonalTrainingSession.member_id == member_id)
                  .first())

        if not session:
            return {'success': False, 'error': 'Session not found'}

        if session.status == SessionStatus.CANCELLED:
            return {'success': False, 'error': 'Session is already cancelled'}

        if session.status == SessionStatus.COMPLETED:
            return {'success': False, 'error': 'Cannot cancel a completed session'}

        if session.scheduled_time <= datetime.now():
            return {'success': False, 'error': 'Cannot cancel a past session'}

        try:
            session.status = SessionStatus.CANCELLED
            self.session.commit()
            return {'success': True, 'message': 'Session cancelled successfully'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def reschedule_pt_session(self, member_id: int, session_id: int, new_time: datetime) -> dict:
        """Reschedule a personal training session."""
        # Get the existing session
        old_session = (self.session.query(PersonalTrainingSession)
                      .filter(PersonalTrainingSession.session_id == session_id)
                      .filter(PersonalTrainingSession.member_id == member_id)
                      .first())

        if not old_session:
            return {'success': False, 'error': 'Session not found'}

        if old_session.status != SessionStatus.SCHEDULED:
            return {'success': False, 'error': 'Can only reschedule scheduled sessions'}

        # Cancel old session and book new one
        old_session.status = SessionStatus.CANCELLED

        result = self.book_personal_training_session(
            member_id=member_id,
            trainer_id=old_session.trainer_id,
            scheduled_time=new_time,
            duration_minutes=old_session.duration_minutes,
            room_id=old_session.room_id,
            notes=old_session.notes
        )

        if result['success']:
            self.session.commit()
            return {'success': True, 'message': 'Session rescheduled successfully', 'data': result['data']}
        else:
            self.session.rollback()
            return result

    # ==================== Group Class Registration Methods ====================

    def get_available_classes(self, from_date: datetime = None) -> list:
        """Get available fitness classes."""
        if from_date is None:
            from_date = datetime.now()

        return (self.session.query(FitnessClass)
                .filter(FitnessClass.scheduled_time >= from_date)
                .filter(FitnessClass.status == ClassStatus.SCHEDULED)
                .order_by(FitnessClass.scheduled_time)
                .all())

    def register_for_class(self, member_id: int, class_id: int) -> dict:
        """
        Register a member for a fitness class.

        Validates:
        - Class exists and is scheduled
        - Class has capacity
        - Member is not already registered
        - No time conflicts with member's other bookings

        Returns:
            dict with 'success' boolean and 'data' or 'error' message
        """
        # Validate member
        member = self.get_member_by_id(member_id)
        if not member:
            return {'success': False, 'error': 'Member not found'}

        # Validate class
        fitness_class = (self.session.query(FitnessClass)
                        .filter(FitnessClass.class_id == class_id)
                        .first())

        if not fitness_class:
            return {'success': False, 'error': 'Class not found'}

        if fitness_class.status != ClassStatus.SCHEDULED:
            return {'success': False, 'error': 'Class is not available for registration'}

        if fitness_class.scheduled_time <= datetime.now():
            return {'success': False, 'error': 'Cannot register for past classes'}

        # Check if already registered
        existing_registration = (self.session.query(ClassRegistration)
                                .filter(ClassRegistration.member_id == member_id)
                                .filter(ClassRegistration.class_id == class_id)
                                .filter(ClassRegistration.status.in_([
                                    RegistrationStatus.REGISTERED,
                                    RegistrationStatus.ATTENDED
                                ]))
                                .first())

        if existing_registration:
            return {'success': False, 'error': 'You are already registered for this class'}

        # Check class capacity
        registered_count = (self.session.query(ClassRegistration)
                           .filter(ClassRegistration.class_id == class_id)
                           .filter(ClassRegistration.status == RegistrationStatus.REGISTERED)
                           .count())

        if registered_count >= fitness_class.capacity:
            return {'success': False, 'error': 'Class is full'}

        # Check for time conflicts with PT sessions
        class_end_time = fitness_class.get_end_time()
        session_conflict = (self.session.query(PersonalTrainingSession)
                          .filter(PersonalTrainingSession.member_id == member_id)
                          .filter(PersonalTrainingSession.status == SessionStatus.SCHEDULED)
                          .filter(PersonalTrainingSession.scheduled_time < class_end_time)
                          .filter(PersonalTrainingSession.scheduled_time >= fitness_class.scheduled_time)
                          .first())

        if session_conflict:
            return {'success': False, 'error': 'You have a conflicting PT session at this time'}

        # Create registration
        try:
            registration = ClassRegistration(
                member_id=member_id,
                class_id=class_id,
                status=RegistrationStatus.REGISTERED
            )
            self.session.add(registration)
            self.session.commit()
            return {'success': True, 'data': registration.to_dict()}
        except IntegrityError:
            self.session.rollback()
            return {'success': False, 'error': 'You are already registered for this class'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_member_class_registrations(self, member_id: int, upcoming_only: bool = True) -> list:
        """Get member's class registrations."""
        query = (self.session.query(ClassRegistration)
                .join(FitnessClass)
                .filter(ClassRegistration.member_id == member_id))

        if upcoming_only:
            query = query.filter(FitnessClass.scheduled_time >= datetime.now())
            query = query.filter(ClassRegistration.status == RegistrationStatus.REGISTERED)

        return query.order_by(FitnessClass.scheduled_time).all()

    def cancel_class_registration(self, member_id: int, registration_id: int) -> dict:
        """Cancel a class registration."""
        registration = (self.session.query(ClassRegistration)
                       .filter(ClassRegistration.registration_id == registration_id)
                       .filter(ClassRegistration.member_id == member_id)
                       .first())

        if not registration:
            return {'success': False, 'error': 'Registration not found'}

        if registration.status == RegistrationStatus.CANCELLED:
            return {'success': False, 'error': 'Registration is already cancelled'}

        if registration.status == RegistrationStatus.ATTENDED:
            return {'success': False, 'error': 'Cannot cancel an attended class'}

        # Check if class has already started
        fitness_class = registration.fitness_class
        if fitness_class.scheduled_time <= datetime.now():
            return {'success': False, 'error': 'Cannot cancel registration for a class that has started'}

        try:
            registration.status = RegistrationStatus.CANCELLED
            self.session.commit()
            return {'success': True, 'message': 'Registration cancelled successfully'}
        except Exception as e:
            self.session.rollback()
            return {'success': False, 'error': str(e)}
