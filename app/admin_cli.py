from datetime import date, time, datetime, timedelta
from services import AdminService, TrainerService
from models import RoomType


class AdminCLI:
    """CLI handler for administrative operations."""

    def __init__(self, session, admin):
        self.session = session
        self.admin = admin
        self.admin_service = AdminService(session)
        self.trainer_service = TrainerService(session)

    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "-" * 50)
        print(f"  {title}")
        print("-" * 50)

    def print_menu(self, options: list):
        """Print a numbered menu."""
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print()

    def run(self):
        """Main admin menu loop."""
        while True:
            self.print_header(f"ADMIN MENU - {self.admin.first_name} {self.admin.last_name}")
            
            options = [
                "Room Management",
                "Class Management",
                "View All Trainers",
                "View All Rooms",
                "Logout"
            ]
            self.print_menu(options)
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                self.room_management()
            elif choice == '2':
                self.class_management()
            elif choice == '3':
                self.view_trainers()
            elif choice == '4':
                self.view_rooms()
            elif choice == '5':
                print("\nLogging out...")
                break
            else:
                print("Invalid choice. Please try again.")

    # ==================== Room Management ====================

    def room_management(self):
        """Room management submenu."""
        while True:
            self.print_header("ROOM MANAGEMENT")
            
            options = [
                "Create New Room",
                "Book a Room",
                "View Room Bookings",
                "Cancel Booking",
                "Check Room Availability",
                "Back to Admin Menu"
            ]
            self.print_menu(options)
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                self.create_room()
            elif choice == '2':
                self.book_room()
            elif choice == '3':
                self.view_room_bookings()
            elif choice == '4':
                self.cancel_booking()
            elif choice == '5':
                self.check_room_availability()
            elif choice == '6':
                break
            else:
                print("Invalid choice.")

    def create_room(self):
        """Create a new room."""
        self.print_header("CREATE NEW ROOM")
        
        name = input("  Room name: ").strip()
        if not name:
            print("  Room name is required.")
            input("\nPress Enter to continue...")
            return
        
        capacity = input("  Capacity: ").strip()
        try:
            capacity = int(capacity)
        except ValueError:
            print("  Invalid capacity.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Room types:")
        for i, rt in enumerate(RoomType, 1):
            print(f"    {i}. {rt.value.replace('_', ' ').title()}")
        
        type_choice = input("\n  Select room type (1-5): ").strip()
        try:
            room_type = list(RoomType)[int(type_choice) - 1]
        except (ValueError, IndexError):
            print("  Invalid room type.")
            input("\nPress Enter to continue...")
            return
        
        result = self.admin_service.create_room(name, capacity, room_type.value)
        
        if result['success']:
            print(f"\n  Room '{name}' created successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def view_rooms(self):
        """View all rooms."""
        self.print_header("ALL ROOMS")
        
        rooms = self.admin_service.get_all_rooms()
        
        if not rooms:
            print("\n  No rooms registered.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  " + "-" * 60)
        print(f"  {'ID':<5} {'Name':<20} {'Type':<15} {'Capacity':<10}")
        print("  " + "-" * 60)
        
        for room in rooms:
            print(f"  {room.room_id:<5} {room.name:<20} "
                  f"{room.room_type.value.replace('_', ' ').title():<15} {room.capacity:<10}")
        
        print("  " + "-" * 60)
        input("\nPress Enter to continue...")

    def book_room(self):
        """Book a room."""
        self.print_header("BOOK A ROOM")
        
        # Show available rooms
        rooms = self.admin_service.get_all_rooms()
        if not rooms:
            print("\n  No rooms available. Please create a room first.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Available rooms:")
        for room in rooms:
            print(f"    [{room.room_id}] {room.name} (Capacity: {room.capacity})")
        
        room_id = input("\n  Enter room ID: ").strip()
        try:
            room_id = int(room_id)
        except ValueError:
            print("  Invalid room ID.")
            input("\nPress Enter to continue...")
            return
        
        date_str = input("  Booking date (YYYY-MM-DD): ").strip()
        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("  Invalid date format.")
            input("\nPress Enter to continue...")
            return
        
        start_str = input("  Start time (HH:MM): ").strip()
        end_str = input("  End time (HH:MM): ").strip()
        
        try:
            start_parts = start_str.split(":")
            end_parts = end_str.split(":")
            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))
        except (ValueError, IndexError):
            print("  Invalid time format.")
            input("\nPress Enter to continue...")
            return
        
        purpose = input("  Purpose (optional): ").strip() or None
        
        result = self.admin_service.book_room(
            room_id=room_id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            purpose=purpose,
            admin_id=self.admin.admin_id
        )
        
        if result['success']:
            print("\n  Room booked successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def view_room_bookings(self):
        """View bookings for a room."""
        self.print_header("ROOM BOOKINGS")
        
        rooms = self.admin_service.get_all_rooms()
        if not rooms:
            print("\n  No rooms registered.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Rooms:")
        for room in rooms:
            print(f"    [{room.room_id}] {room.name}")
        
        room_id = input("\n  Enter room ID (or 'all'): ").strip()
        
        if room_id.lower() == 'all':
            for room in rooms:
                self._show_room_bookings(room.room_id, room.name)
        else:
            try:
                room_id = int(room_id)
                room = self.admin_service.get_room_by_id(room_id)
                if room:
                    self._show_room_bookings(room_id, room.name)
                else:
                    print("  Room not found.")
            except ValueError:
                print("  Invalid input.")
        
        input("\nPress Enter to continue...")

    def _show_room_bookings(self, room_id: int, room_name: str):
        """Helper to display bookings for a room."""
        bookings = self.admin_service.get_room_bookings(room_id, from_date=date.today())
        
        print(f"\n  --- Bookings for {room_name} ---")
        if not bookings:
            print("    No upcoming bookings.")
            return
        
        for booking in bookings:
            print(f"    [{booking.booking_id}] {booking.booking_date} "
                  f"{str(booking.start_time)[:5]}-{str(booking.end_time)[:5]} "
                  f"({booking.status.value})")
            if booking.purpose:
                print(f"         Purpose: {booking.purpose}")

    def cancel_booking(self):
        """Cancel a room booking."""
        self.print_header("CANCEL BOOKING")
        
        booking_id = input("  Enter booking ID to cancel: ").strip()
        try:
            booking_id = int(booking_id)
        except ValueError:
            print("  Invalid booking ID.")
            input("\nPress Enter to continue...")
            return
        
        confirm = input("  Are you sure? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        result = self.admin_service.cancel_room_booking(booking_id)
        
        if result['success']:
            print("\n  Booking cancelled successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def check_room_availability(self):
        """Check if a room is available."""
        self.print_header("CHECK ROOM AVAILABILITY")
        
        rooms = self.admin_service.get_all_rooms()
        if not rooms:
            print("\n  No rooms registered.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Rooms:")
        for room in rooms:
            print(f"    [{room.room_id}] {room.name}")
        
        room_id = input("\n  Enter room ID: ").strip()
        try:
            room_id = int(room_id)
        except ValueError:
            print("  Invalid room ID.")
            input("\nPress Enter to continue...")
            return
        
        date_str = input("  Date to check (YYYY-MM-DD): ").strip()
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("  Invalid date format.")
            input("\nPress Enter to continue...")
            return
        
        start_str = input("  Start time (HH:MM): ").strip()
        end_str = input("  End time (HH:MM): ").strip()
        
        try:
            start_parts = start_str.split(":")
            end_parts = end_str.split(":")
            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))
        except (ValueError, IndexError):
            print("  Invalid time format.")
            input("\nPress Enter to continue...")
            return
        
        is_available = self.admin_service.is_room_available(
            room_id, check_date, start_time, end_time
        )
        
        if is_available:
            print("\n  ✓ Room is AVAILABLE for the requested time slot!")
        else:
            print("\n  ✗ Room is NOT AVAILABLE - there is a conflicting booking.")
        
        input("\nPress Enter to continue...")

    # ==================== Class Management ====================

    def class_management(self):
        """Class management submenu."""
        while True:
            self.print_header("CLASS MANAGEMENT")
            
            options = [
                "Create New Class",
                "View All Classes",
                "Update Class",
                "Cancel Class",
                "Back to Admin Menu"
            ]
            self.print_menu(options)
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                self.create_class()
            elif choice == '2':
                self.view_classes()
            elif choice == '3':
                self.update_class()
            elif choice == '4':
                self.cancel_class()
            elif choice == '5':
                break
            else:
                print("Invalid choice.")

    def create_class(self):
        """Create a new fitness class."""
        self.print_header("CREATE NEW CLASS")
        
        # Show trainers
        trainers = self.trainer_service.get_all_trainers()
        if not trainers:
            print("\n  No trainers available. Please register trainers first.")
            input("\nPress Enter to continue...")
            return
        
        # Show rooms
        rooms = self.admin_service.get_all_rooms()
        if not rooms:
            print("\n  No rooms available. Please create rooms first.")
            input("\nPress Enter to continue...")
            return
        
        name = input("  Class name: ").strip()
        if not name:
            print("  Class name is required.")
            input("\nPress Enter to continue...")
            return
        
        description = input("  Description (optional): ").strip() or None
        
        print("\n  Available trainers:")
        for trainer in trainers:
            print(f"    [{trainer.trainer_id}] {trainer.first_name} {trainer.last_name} "
                  f"({trainer.specialization or 'General'})")
        
        trainer_id = input("\n  Select trainer ID: ").strip()
        try:
            trainer_id = int(trainer_id)
        except ValueError:
            print("  Invalid trainer ID.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Available rooms:")
        for room in rooms:
            print(f"    [{room.room_id}] {room.name} (Capacity: {room.capacity})")
        
        room_id = input("\n  Select room ID: ").strip()
        try:
            room_id = int(room_id)
        except ValueError:
            print("  Invalid room ID.")
            input("\nPress Enter to continue...")
            return
        
        datetime_str = input("  Scheduled time (YYYY-MM-DD HH:MM): ").strip()
        try:
            scheduled_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("  Invalid datetime format.")
            input("\nPress Enter to continue...")
            return
        
        duration = input("  Duration in minutes [60]: ").strip()
        duration_minutes = int(duration) if duration else 60
        
        capacity = input("  Capacity (leave blank for room max): ").strip()
        capacity = int(capacity) if capacity else None
        
        result = self.admin_service.create_class(
            name=name,
            trainer_id=trainer_id,
            room_id=room_id,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            capacity=capacity,
            description=description
        )
        
        if result['success']:
            print(f"\n  Class '{name}' created successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def view_classes(self):
        """View all fitness classes."""
        self.print_header("ALL FITNESS CLASSES")
        
        include_past = input("  Include past classes? (y/n) [n]: ").strip().lower() == 'y'
        
        classes = self.admin_service.get_all_classes(include_past=include_past)
        
        if not classes:
            print("\n  No classes found.")
            input("\nPress Enter to continue...")
            return
        
        for cls in classes:
            print(f"\n  [{cls.class_id}] {cls.name}")
            print(f"      Time: {cls.scheduled_time}")
            print(f"      Duration: {cls.duration_minutes} min")
            print(f"      Room ID: {cls.room_id}")
            print(f"      Trainer ID: {cls.trainer_id}")
            print(f"      Capacity: {cls.current_registration_count()}/{cls.capacity}")
            print(f"      Status: {cls.status.value}")
        
        input("\nPress Enter to continue...")

    def view_trainers(self):
        """View all trainers."""
        self.print_header("ALL TRAINERS")
        
        trainers = self.trainer_service.get_all_trainers()
        
        if not trainers:
            print("\n  No trainers registered.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  " + "-" * 70)
        print(f"  {'ID':<5} {'Name':<25} {'Specialization':<25} {'Phone':<15}")
        print("  " + "-" * 70)
        
        for trainer in trainers:
            name = f"{trainer.first_name} {trainer.last_name}"
            spec = trainer.specialization or "General"
            phone = trainer.phone or "-"
            print(f"  {trainer.trainer_id:<5} {name:<25} {spec:<25} {phone:<15}")
        
        print("  " + "-" * 70)
        input("\nPress Enter to continue...")

    def update_class(self):
        """Update a fitness class."""
        self.print_header("UPDATE CLASS")
        
        class_id = input("  Enter class ID to update: ").strip()
        try:
            class_id = int(class_id)
        except ValueError:
            print("  Invalid class ID.")
            input("\nPress Enter to continue...")
            return
        
        fitness_class = self.admin_service.get_class_by_id(class_id)
        if not fitness_class:
            print("  Class not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n  Current class: {fitness_class.name}")
        print("  Enter new values (leave blank to keep current):")
        
        new_name = input(f"  Name [{fitness_class.name}]: ").strip()
        new_capacity = input(f"  Capacity [{fitness_class.capacity}]: ").strip()
        
        updates = {}
        if new_name:
            updates['name'] = new_name
        if new_capacity:
            updates['capacity'] = int(new_capacity)
        
        if updates:
            result = self.admin_service.update_class(class_id, **updates)
            if result['success']:
                print("\n  Class updated successfully!")
            else:
                print(f"\n  Error: {result['error']}")
        else:
            print("\n  No changes made.")
        
        input("\nPress Enter to continue...")

    def cancel_class(self):
        """Cancel a fitness class."""
        self.print_header("CANCEL CLASS")
        
        class_id = input("  Enter class ID to cancel: ").strip()
        try:
            class_id = int(class_id)
        except ValueError:
            print("  Invalid class ID.")
            input("\nPress Enter to continue...")
            return
        
        fitness_class = self.admin_service.get_class_by_id(class_id)
        if not fitness_class:
            print("  Class not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n  Class: {fitness_class.name}")
        print(f"  Scheduled: {fitness_class.scheduled_time}")
        
        confirm = input("\n  Are you sure you want to cancel? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        result = self.admin_service.cancel_class(class_id)
        
        if result['success']:
            print("\n  Class cancelled successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")
