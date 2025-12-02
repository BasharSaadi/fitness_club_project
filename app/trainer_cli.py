from datetime import time, datetime
from services import TrainerService, MemberService
from models import DayOfWeek


class TrainerCLI:
    """CLI handler for trainer operations."""

    def __init__(self, session, trainer):
        self.session = session
        self.trainer = trainer
        self.trainer_service = TrainerService(session)
        self.member_service = MemberService(session)

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
        """Main trainer menu loop."""
        while True:
            self.print_header(f"TRAINER MENU - {self.trainer.first_name} {self.trainer.last_name}")
            
            options = [
                "View My Schedule",
                "Set Availability",
                "View My Availability",
                "Delete Availability Slot",
                "Member Lookup",
                "Logout"
            ]
            self.print_menu(options)
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                self.view_schedule()
            elif choice == '2':
                self.set_availability()
            elif choice == '3':
                self.view_availability()
            elif choice == '4':
                self.delete_availability()
            elif choice == '5':
                self.member_lookup()
            elif choice == '6':
                print("\nLogging out...")
                break
            else:
                print("Invalid choice. Please try again.")

    def view_schedule(self):
        """View trainer's complete schedule."""
        self.print_header("MY SCHEDULE")
        
        result = self.trainer_service.get_schedule(self.trainer.trainer_id)
        
        if not result['success']:
            print(f"Error: {result['error']}")
            input("\nPress Enter to continue...")
            return
        
        data = result['data']
        
        # Show availability
        print("\n  --- Weekly Availability ---")
        if data['availability']:
            current_day = None
            for slot in data['availability']:
                day = slot['day_of_week']
                if day != current_day:
                    print(f"\n  {day}:")
                    current_day = day
                print(f"    {slot['start_time']} - {slot['end_time']}")
        else:
            print("  No availability slots set.")
        
        # Show upcoming classes
        print("\n  --- Upcoming Classes ---")
        if data['upcoming_classes']:
            for cls in data['upcoming_classes']:
                print(f"\n  Class: {cls['name']}")
                print(f"    Time: {cls['scheduled_time']}")
                print(f"    Duration: {cls['duration_minutes']} minutes")
                print(f"    Capacity: {cls['capacity']}")
        else:
            print("  No upcoming classes assigned.")
        
        input("\nPress Enter to continue...")

    def set_availability(self):
        """Set a new availability slot."""
        self.print_header("SET AVAILABILITY")
        
        print("\n  Days of the week:")
        for i, day in enumerate(DayOfWeek, 1):
            print(f"    {i}. {day.name.title()}")
        
        day_choice = input("\n  Select day (1-7): ").strip()
        try:
            day_enum = list(DayOfWeek)[int(day_choice) - 1]
        except (ValueError, IndexError):
            print("  Invalid day selection.")
            input("\nPress Enter to continue...")
            return
        
        start_str = input("  Start time (HH:MM, 24h format): ").strip()
        end_str = input("  End time (HH:MM, 24h format): ").strip()
        
        try:
            start_parts = start_str.split(":")
            end_parts = end_str.split(":")
            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))
        except (ValueError, IndexError):
            print("  Invalid time format. Use HH:MM (e.g., 09:00)")
            input("\nPress Enter to continue...")
            return
        
        result = self.trainer_service.set_availability(
            trainer_id=self.trainer.trainer_id,
            day_of_week=day_enum.name,
            start_time=start_time,
            end_time=end_time
        )
        
        if result['success']:
            print("\n  Availability slot added successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def view_availability(self):
        """View all availability slots."""
        self.print_header("MY AVAILABILITY")
        
        slots = self.trainer_service.get_availability(self.trainer.trainer_id)
        
        if not slots:
            print("\n  No availability slots set.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  " + "-" * 50)
        print(f"  {'ID':<6} {'Day':<12} {'Start':<10} {'End':<10}")
        print("  " + "-" * 50)
        
        for slot in slots:
            print(f"  {slot.availability_id:<6} {slot.day_of_week.name.title():<12} "
                  f"{str(slot.start_time)[:5]:<10} {str(slot.end_time)[:5]:<10}")
        
        print("  " + "-" * 50)
        input("\nPress Enter to continue...")

    def delete_availability(self):
        """Delete an availability slot."""
        self.print_header("DELETE AVAILABILITY")
        
        slots = self.trainer_service.get_availability(self.trainer.trainer_id)
        
        if not slots:
            print("\n  No availability slots to delete.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Current slots:")
        for slot in slots:
            print(f"    [{slot.availability_id}] {slot.day_of_week.name.title()} "
                  f"{str(slot.start_time)[:5]} - {str(slot.end_time)[:5]}")
        
        slot_id = input("\n  Enter slot ID to delete: ").strip()
        try:
            slot_id = int(slot_id)
        except ValueError:
            print("  Invalid ID.")
            input("\nPress Enter to continue...")
            return
        
        confirm = input("  Are you sure? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        result = self.trainer_service.delete_availability(self.trainer.trainer_id, slot_id)
        
        if result['success']:
            print("\n  Availability slot deleted!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def member_lookup(self):
        """Look up member information (read-only)."""
        self.print_header("MEMBER LOOKUP")
        
        print("\n  Search for members by name (case-insensitive)")
        query = input("  Enter name to search: ").strip()
        
        if not query:
            print("  Please enter a search term.")
            input("\nPress Enter to continue...")
            return
        
        members = self.member_service.search_members(query)
        
        if not members:
            print(f"\n  No members found matching '{query}'")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n  Found {len(members)} member(s):\n")
        
        for member in members:
            print(f"  --- {member.first_name} {member.last_name} ---")
            print(f"  Email: {member.email}")
            
            # Get active goal (read-only access)
            goals = self.member_service.get_active_goals(member.member_id)
            if goals:
                goal = goals[0]  # Show first active goal
                print(f"  Current Goal: {goal.goal_type.value.replace('_', ' ').title()}")
                print(f"    Target: {goal.target_value}")
                if goal.current_value:
                    print(f"    Current: {goal.current_value}")
            else:
                print("  Current Goal: None set")
            
            # Get last health metric (read-only access)
            last_metric = self.member_service.get_latest_health_metric(member.member_id)
            if last_metric:
                print(f"  Last Metric ({last_metric.recorded_at.strftime('%Y-%m-%d')}):")
                if last_metric.weight_kg:
                    print(f"    Weight: {last_metric.weight_kg} kg")
                if last_metric.body_fat_percentage:
                    print(f"    Body Fat: {last_metric.body_fat_percentage}%")
            else:
                print("  Last Metric: No data recorded")
            
            print()
        
        print("  Note: Trainers have read-only access to member data.")
        input("\nPress Enter to continue...")
