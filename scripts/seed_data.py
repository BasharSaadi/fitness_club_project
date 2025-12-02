import sys
import os
from datetime import datetime, date, time, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    init_db, get_session, drop_db,
    Member, Gender, Trainer, Admin, Room, RoomType,
    HealthMetric, FitnessGoal, GoalType, GoalStatus,
    TrainerAvailability, DayOfWeek, FitnessClass, ClassStatus,
    RoomBooking, BookingStatus, ClassRegistration, RegistrationStatus
)
from services import MemberService, TrainerService, AdminService


def seed_database():
    """Seed the database with sample data."""
    print("=" * 60)
    print("  SEEDING DATABASE WITH SAMPLE DATA")
    print("=" * 60)
    
    session = get_session()
    
    try:
        # Initialize database tables
        print("\n1. Initializing database tables...")
        init_db()
        
        # ==================== Seed Admins ====================
        print("\n2. Creating admin accounts...")
        admin_service = AdminService(session)
        
        admins_data = [
            {"email": "admin@fitnessclub.com", "password": "admin123", "first_name": "Sarah", "last_name": "Manager"},
            {"email": "staff@fitnessclub.com", "password": "staff123", "first_name": "Mike", "last_name": "Staff"},
            {"email": "supervisor@fitnessclub.com", "password": "super123", "first_name": "Emily", "last_name": "Supervisor"},
        ]
        
        for admin_data in admins_data:
            result = admin_service.register_admin(**admin_data)
            if result['success']:
                print(f"   ✓ Created admin: {admin_data['email']}")
            else:
                print(f"   - Skipped {admin_data['email']}: {result['error']}")
        
        # ==================== Seed Rooms ====================
        print("\n3. Creating rooms...")
        
        rooms_data = [
            {"name": "Studio A", "capacity": 30, "room_type": "studio"},
            {"name": "Studio B", "capacity": 20, "room_type": "studio"},
            {"name": "Main Gym Floor", "capacity": 100, "room_type": "gym_floor"},
            {"name": "Training Room 1", "capacity": 10, "room_type": "training_room"},
            {"name": "Training Room 2", "capacity": 8, "room_type": "training_room"},
        ]
        
        for room_data in rooms_data:
            result = admin_service.create_room(**room_data)
            if result['success']:
                print(f"   ✓ Created room: {room_data['name']}")
            else:
                print(f"   - Skipped {room_data['name']}: {result['error']}")
        
        # ==================== Seed Trainers ====================
        print("\n4. Creating trainer accounts...")
        trainer_service = TrainerService(session)
        
        trainers_data = [
            {"email": "john.yoga@fitnessclub.com", "password": "trainer123", "first_name": "John", 
             "last_name": "Smith", "specialization": "Yoga, Meditation", "phone": "555-0101"},
            {"email": "lisa.strength@fitnessclub.com", "password": "trainer123", "first_name": "Lisa", 
             "last_name": "Johnson", "specialization": "Strength Training, HIIT", "phone": "555-0102"},
            {"email": "carlos.cardio@fitnessclub.com", "password": "trainer123", "first_name": "Carlos", 
             "last_name": "Garcia", "specialization": "Cardio, Spinning", "phone": "555-0103"},
            {"email": "emma.pilates@fitnessclub.com", "password": "trainer123", "first_name": "Emma", 
             "last_name": "Wilson", "specialization": "Pilates, Flexibility", "phone": "555-0104"},
        ]
        
        for trainer_data in trainers_data:
            result = trainer_service.register_trainer(**trainer_data)
            if result['success']:
                print(f"   ✓ Created trainer: {trainer_data['first_name']} {trainer_data['last_name']}")
            else:
                print(f"   - Skipped {trainer_data['email']}: {result['error']}")
        
        # ==================== Seed Trainer Availability ====================
        print("\n5. Setting trainer availability...")
        
        # Get trainer IDs
        trainers = trainer_service.get_all_trainers()
        if trainers:
            trainer_john = trainers[0]
            
            availability_data = [
                {"day_of_week": "MONDAY", "start_time": time(9, 0), "end_time": time(12, 0)},
                {"day_of_week": "MONDAY", "start_time": time(14, 0), "end_time": time(18, 0)},
                {"day_of_week": "WEDNESDAY", "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": "FRIDAY", "start_time": time(10, 0), "end_time": time(15, 0)},
            ]
            
            for avail in availability_data:
                result = trainer_service.set_availability(trainer_john.trainer_id, **avail)
                if result['success']:
                    print(f"   ✓ Set availability: {avail['day_of_week']} {avail['start_time']}-{avail['end_time']}")
        
        # ==================== Seed Members ====================
        print("\n6. Creating member accounts...")
        member_service = MemberService(session)
        
        members_data = [
            {"email": "alice@email.com", "password": "member123", "first_name": "Alice", 
             "last_name": "Brown", "date_of_birth": date(1990, 5, 15), "gender": "female", "phone": "555-1001"},
            {"email": "bob@email.com", "password": "member123", "first_name": "Bob", 
             "last_name": "Davis", "date_of_birth": date(1985, 8, 22), "gender": "male", "phone": "555-1002"},
            {"email": "carol@email.com", "password": "member123", "first_name": "Carol", 
             "last_name": "Martinez", "date_of_birth": date(1995, 3, 10), "gender": "female", "phone": "555-1003"},
            {"email": "david@email.com", "password": "member123", "first_name": "David", 
             "last_name": "Taylor", "date_of_birth": date(1988, 11, 5), "gender": "male", "phone": "555-1004"},
            {"email": "eve@email.com", "password": "member123", "first_name": "Eve", 
             "last_name": "Anderson", "date_of_birth": date(1992, 7, 28), "gender": "female", "phone": "555-1005"},
        ]
        
        for member_data in members_data:
            result = member_service.register_member(**member_data)
            if result['success']:
                print(f"   ✓ Created member: {member_data['first_name']} {member_data['last_name']}")
            else:
                print(f"   - Skipped {member_data['email']}: {result['error']}")
        
        # ==================== Seed Health Metrics ====================
        print("\n7. Adding health metrics...")
        
        # Get member IDs
        members = session.query(Member).all()
        if members:
            alice = members[0]
            
            # Add multiple health metrics over time (to show history)
            metrics_data = [
                {"weight_kg": 70.5, "height_cm": 165, "heart_rate_bpm": 72, "body_fat_percentage": 25.0},
                {"weight_kg": 69.8, "height_cm": 165, "heart_rate_bpm": 70, "body_fat_percentage": 24.5},
                {"weight_kg": 69.2, "height_cm": 165, "heart_rate_bpm": 68, "body_fat_percentage": 24.0},
                {"weight_kg": 68.5, "height_cm": 165, "heart_rate_bpm": 66, "body_fat_percentage": 23.5},
            ]
            
            for i, metric in enumerate(metrics_data):
                # Add metrics with different timestamps
                health_metric = HealthMetric(
                    member_id=alice.member_id,
                    **metric,
                    recorded_at=datetime.now() - timedelta(days=(len(metrics_data) - i) * 7)
                )
                session.add(health_metric)
                print(f"   ✓ Added health metric for Alice (Week -{len(metrics_data) - i})")
            
            session.commit()
        
        # ==================== Seed Fitness Goals ====================
        print("\n8. Creating fitness goals...")
        
        if members:
            alice = members[0]
            
            goals_data = [
                {"goal_type": "weight_loss", "target_value": 65.0, "current_value": 68.5, 
                 "deadline": date.today() + timedelta(days=90)},
                {"goal_type": "body_fat_reduction", "target_value": 20.0, "current_value": 23.5,
                 "deadline": date.today() + timedelta(days=120)},
            ]
            
            for goal in goals_data:
                result = member_service.create_fitness_goal(alice.member_id, **goal)
                if result['success']:
                    print(f"   ✓ Created goal: {goal['goal_type']}")
        
        # ==================== Seed Fitness Classes ====================
        print("\n9. Creating fitness classes...")
        
        rooms = admin_service.get_all_rooms()
        trainers = trainer_service.get_all_trainers()
        
        if rooms and trainers:
            classes_data = [
                {"name": "Morning Yoga", "trainer_id": trainers[0].trainer_id, "room_id": rooms[0].room_id,
                 "scheduled_time": datetime.now() + timedelta(days=1, hours=9), "duration_minutes": 60,
                 "description": "Relaxing morning yoga session for all levels"},
                {"name": "HIIT Blast", "trainer_id": trainers[1].trainer_id, "room_id": rooms[1].room_id,
                 "scheduled_time": datetime.now() + timedelta(days=1, hours=18), "duration_minutes": 45,
                 "description": "High-intensity interval training"},
                {"name": "Spin Class", "trainer_id": trainers[2].trainer_id, "room_id": rooms[0].room_id,
                 "scheduled_time": datetime.now() + timedelta(days=2, hours=17), "duration_minutes": 50,
                 "description": "Indoor cycling workout"},
                {"name": "Pilates Core", "trainer_id": trainers[3].trainer_id, "room_id": rooms[1].room_id,
                 "scheduled_time": datetime.now() + timedelta(days=3, hours=10), "duration_minutes": 55,
                 "description": "Core strengthening Pilates class"},
            ]
            
            for cls_data in classes_data:
                result = admin_service.create_class(**cls_data)
                if result['success']:
                    print(f"   ✓ Created class: {cls_data['name']}")
                else:
                    print(f"   - Skipped {cls_data['name']}: {result['error']}")
        
        # ==================== Seed Room Bookings ====================
        print("\n10. Creating room bookings...")
        
        if rooms:
            bookings_data = [
                {"room_id": rooms[3].room_id, "booking_date": date.today() + timedelta(days=1),
                 "start_time": time(14, 0), "end_time": time(15, 0), "purpose": "Personal Training Session"},
                {"room_id": rooms[4].room_id, "booking_date": date.today() + timedelta(days=2),
                 "start_time": time(10, 0), "end_time": time(11, 30), "purpose": "Private Yoga Session"},
            ]
            
            for booking in bookings_data:
                result = admin_service.book_room(**booking)
                if result['success']:
                    print(f"   ✓ Booked room: {booking['purpose']}")
                else:
                    print(f"   - Skipped booking: {result['error']}")
        
        print("\n" + "=" * 60)
        print("  DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        
        print("\n  Sample Login Credentials:")
        print("  " + "-" * 40)
        print("  Members:")
        print("    Email: alice@email.com")
        print("    Password: member123")
        print("  " + "-" * 40)
        print("  Trainers:")
        print("    Email: john.yoga@fitnessclub.com")
        print("    Password: trainer123")
        print("  " + "-" * 40)
        print("  Admins:")
        print("    Email: admin@fitnessclub.com")
        print("    Password: admin123")
        print("  " + "-" * 40)
        
    except Exception as e:
        print(f"\nError seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def reset_database():
    """Drop all tables and reseed."""
    print("\nWARNING: This will delete all existing data!")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        print("\nDropping all tables...")
        drop_db()
        print("Reseeding database...")
        seed_database()
    else:
        print("Cancelled.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed the database with sample data')
    parser.add_argument('--reset', action='store_true', help='Drop and recreate all tables')
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        seed_database()
