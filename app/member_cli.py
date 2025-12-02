from datetime import date, datetime
from services import MemberService
from models import GoalType


class MemberCLI:
    """CLI handler for member operations."""

    def __init__(self, session, member):
        self.session = session
        self.member = member
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
        """Main member menu loop."""
        while True:
            self.print_header(f"MEMBER MENU - {self.member.first_name} {self.member.last_name}")

            options = [
                "View Dashboard",
                "Update Profile",
                "Log Health Metrics",
                "View Health History",
                "Manage Fitness Goals",
                "Book Personal Training Session",
                "Register for Group Classes",
                "Logout"
            ]
            self.print_menu(options)

            choice = input("Select option (1-8): ").strip()

            if choice == '1':
                self.view_dashboard()
            elif choice == '2':
                self.update_profile()
            elif choice == '3':
                self.log_health_metrics()
            elif choice == '4':
                self.view_health_history()
            elif choice == '5':
                self.manage_goals()
            elif choice == '6':
                self.manage_pt_sessions()
            elif choice == '7':
                self.manage_class_registrations()
            elif choice == '8':
                print("\nLogging out...")
                break
            else:
                print("Invalid choice. Please try again.")

    def view_dashboard(self):
        """Display member dashboard with summary information."""
        self.print_header("YOUR DASHBOARD")
        
        result = self.member_service.get_dashboard_data(self.member.member_id)
        
        if not result['success']:
            print(f"Error: {result['error']}")
            return
        
        data = result['data']
        member = data['member']
        
        print(f"\n  Welcome, {member['first_name']} {member['last_name']}!")
        print(f"  Member since: {member['created_at'][:10]}")
        
        print("\n  --- Latest Health Metrics ---")
        if data['latest_metric']:
            metric = data['latest_metric']
            print(f"  Weight: {metric['weight_kg'] or 'N/A'} kg")
            print(f"  Height: {metric['height_cm'] or 'N/A'} cm")
            print(f"  Heart Rate: {metric['heart_rate_bpm'] or 'N/A'} bpm")
            print(f"  Body Fat: {metric['body_fat_percentage'] or 'N/A'}%")
            print(f"  Recorded: {metric['recorded_at'][:10]}")
        else:
            print("  No health metrics recorded yet.")
        
        print("\n  --- Fitness Goals ---")
        if data['active_goals']:
            for goal in data['active_goals']:
                progress = ""
                if goal['current_value']:
                    progress = f" (Current: {goal['current_value']})"
                print(f"  • {goal['goal_type'].replace('_', ' ').title()}: Target {goal['target_value']}{progress}")
        else:
            print("  No active fitness goals.")
        
        print("\n  --- Activity Summary ---")
        print(f"  Total health entries: {data['health_history_count']}")
        print(f"  Classes registered: {data['past_class_count']}")
        
        input("\nPress Enter to continue...")

    def update_profile(self):
        """Update member profile information."""
        self.print_header("UPDATE PROFILE")
        
        print(f"\n  Current Profile:")
        print(f"  First Name: {self.member.first_name}")
        print(f"  Last Name: {self.member.last_name}")
        print(f"  Phone: {self.member.phone or 'Not set'}")
        print(f"  Date of Birth: {self.member.date_of_birth or 'Not set'}")
        print(f"  Gender: {self.member.gender.value if self.member.gender else 'Not set'}")
        
        print("\n  Enter new values (leave blank to keep current):")
        
        first_name = input(f"  First Name [{self.member.first_name}]: ").strip()
        last_name = input(f"  Last Name [{self.member.last_name}]: ").strip()
        phone = input(f"  Phone [{self.member.phone or ''}]: ").strip()
        
        updates = {}
        if first_name:
            updates['first_name'] = first_name
        if last_name:
            updates['last_name'] = last_name
        if phone:
            updates['phone'] = phone
        
        if updates:
            result = self.member_service.update_profile(self.member.member_id, **updates)
            if result['success']:
                print("\n  Profile updated successfully!")
                # Refresh member object
                self.member = self.member_service.get_member_by_id(self.member.member_id)
            else:
                print(f"\n  Error: {result['error']}")
        else:
            print("\n  No changes made.")
        
        input("\nPress Enter to continue...")

    def log_health_metrics(self):
        """Log new health metrics."""
        self.print_header("LOG HEALTH METRICS")
        
        print("\n  Enter your current health metrics (leave blank to skip):\n")
        
        weight = input("  Weight (kg): ").strip()
        height = input("  Height (cm): ").strip()
        heart_rate = input("  Resting Heart Rate (bpm): ").strip()
        body_fat = input("  Body Fat Percentage: ").strip()
        
        # Parse inputs
        weight_kg = float(weight) if weight else None
        height_cm = float(height) if height else None
        heart_rate_bpm = int(heart_rate) if heart_rate else None
        body_fat_pct = float(body_fat) if body_fat else None
        
        if not any([weight_kg, height_cm, heart_rate_bpm, body_fat_pct]):
            print("\n  No metrics entered.")
            input("\nPress Enter to continue...")
            return
        
        result = self.member_service.log_health_metric(
            member_id=self.member.member_id,
            weight_kg=weight_kg,
            height_cm=height_cm,
            heart_rate_bpm=heart_rate_bpm,
            body_fat_percentage=body_fat_pct
        )
        
        if result['success']:
            print("\n  Health metrics logged successfully!")
            print("  (Note: Previous entries are preserved - no overwriting)")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def view_health_history(self):
        """View health metric history."""
        self.print_header("HEALTH HISTORY")
        
        history = self.member_service.get_health_history(self.member.member_id, limit=10)
        
        if not history:
            print("\n  No health metrics recorded yet.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n  Showing last {len(history)} entries:\n")
        print("  " + "-" * 70)
        print(f"  {'Date':<12} {'Weight':<10} {'Height':<10} {'Heart Rate':<12} {'Body Fat':<10}")
        print("  " + "-" * 70)
        
        for metric in history:
            date_str = metric.recorded_at.strftime("%Y-%m-%d")
            weight = f"{metric.weight_kg} kg" if metric.weight_kg else "-"
            height = f"{metric.height_cm} cm" if metric.height_cm else "-"
            hr = f"{metric.heart_rate_bpm} bpm" if metric.heart_rate_bpm else "-"
            bf = f"{metric.body_fat_percentage}%" if metric.body_fat_percentage else "-"
            print(f"  {date_str:<12} {weight:<10} {height:<10} {hr:<12} {bf:<10}")
        
        print("  " + "-" * 70)
        input("\nPress Enter to continue...")

    def manage_goals(self):
        """Manage fitness goals submenu."""
        while True:
            self.print_header("FITNESS GOALS")
            
            options = [
                "View Active Goals",
                "Create New Goal",
                "Update Goal Progress",
                "Back to Member Menu"
            ]
            self.print_menu(options)
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                self.view_goals()
            elif choice == '2':
                self.create_goal()
            elif choice == '3':
                self.update_goal_progress()
            elif choice == '4':
                break
            else:
                print("Invalid choice.")

    def view_goals(self):
        """View active fitness goals."""
        self.print_header("ACTIVE GOALS")
        
        goals = self.member_service.get_active_goals(self.member.member_id)
        
        if not goals:
            print("\n  No active fitness goals.")
            input("\nPress Enter to continue...")
            return
        
        for goal in goals:
            print(f"\n  Goal ID: {goal.goal_id}")
            print(f"  Type: {goal.goal_type.value.replace('_', ' ').title()}")
            print(f"  Target: {goal.target_value}")
            print(f"  Current: {goal.current_value or 'Not set'}")
            print(f"  Deadline: {goal.deadline or 'Not set'}")
            print(f"  Status: {goal.status.value}")
        
        input("\nPress Enter to continue...")

    def create_goal(self):
        """Create a new fitness goal."""
        self.print_header("CREATE NEW GOAL")
        
        print("\n  Available goal types:")
        for i, goal_type in enumerate(GoalType, 1):
            print(f"    {i}. {goal_type.value.replace('_', ' ').title()}")
        
        type_choice = input("\n  Select goal type (1-7): ").strip()
        try:
            goal_type = list(GoalType)[int(type_choice) - 1]
        except (ValueError, IndexError):
            print("  Invalid selection.")
            input("\nPress Enter to continue...")
            return
        
        target = input("  Target value: ").strip()
        try:
            target_value = float(target)
        except ValueError:
            print("  Invalid target value.")
            input("\nPress Enter to continue...")
            return
        
        current = input("  Current value (optional): ").strip()
        current_value = float(current) if current else None
        
        deadline_str = input("  Deadline (YYYY-MM-DD, optional): ").strip()
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            except ValueError:
                print("  Invalid date format.")
                input("\nPress Enter to continue...")
                return
        
        result = self.member_service.create_fitness_goal(
            member_id=self.member.member_id,
            goal_type=goal_type.value,
            target_value=target_value,
            current_value=current_value,
            deadline=deadline
        )
        
        if result['success']:
            print("\n  Fitness goal created successfully!")
        else:
            print(f"\n  Error: {result['error']}")
        
        input("\nPress Enter to continue...")

    def update_goal_progress(self):
        """Update progress on an existing goal."""
        self.print_header("UPDATE GOAL PROGRESS")
        
        goals = self.member_service.get_active_goals(self.member.member_id)
        
        if not goals:
            print("\n  No active goals to update.")
            input("\nPress Enter to continue...")
            return
        
        print("\n  Active Goals:")
        for goal in goals:
            print(f"    [{goal.goal_id}] {goal.goal_type.value.replace('_', ' ').title()} - Target: {goal.target_value}")
        
        goal_id = input("\n  Enter Goal ID to update: ").strip()
        try:
            goal_id = int(goal_id)
        except ValueError:
            print("  Invalid ID.")
            input("\nPress Enter to continue...")
            return
        
        new_value = input("  New current value: ").strip()
        try:
            current_value = float(new_value)
        except ValueError:
            print("  Invalid value.")
            input("\nPress Enter to continue...")
            return
        
        result = self.member_service.update_goal(
            goal_id=goal_id,
            member_id=self.member.member_id,
            current_value=current_value
        )

        if result['success']:
            print("\n  Goal progress updated!")
        else:
            print(f"\n  Error: {result['error']}")

        input("\nPress Enter to continue...")

    # ==================== Personal Training Sessions ====================

    def manage_pt_sessions(self):
        """Personal training session management submenu."""
        while True:
            self.print_header("PERSONAL TRAINING SESSIONS")

            options = [
                "View My PT Sessions",
                "Book New PT Session",
                "Cancel PT Session",
                "Back to Main Menu"
            ]
            self.print_menu(options)

            choice = input("Select option (1-4): ").strip()

            if choice == '1':
                self.view_pt_sessions()
            elif choice == '2':
                self.book_pt_session()
            elif choice == '3':
                self.cancel_pt_session()
            elif choice == '4':
                break
            else:
                print("Invalid choice.")

    def view_pt_sessions(self):
        """View member's personal training sessions."""
        self.print_header("MY PERSONAL TRAINING SESSIONS")

        sessions = self.member_service.get_member_pt_sessions(self.member.member_id)

        if not sessions:
            print("\n  No upcoming PT sessions scheduled.")
            input("\nPress Enter to continue...")
            return

        print(f"\n  You have {len(sessions)} upcoming session(s):\n")
        print("  " + "-" * 80)
        print(f"  {'ID':<5} {'Trainer':<20} {'Date/Time':<20} {'Duration':<10} {'Room':<10}")
        print("  " + "-" * 80)

        for session in sessions:
            trainer = session.trainer
            trainer_name = f"{trainer.first_name} {trainer.last_name}"
            date_time = session.scheduled_time.strftime("%Y-%m-%d %H:%M")
            duration = f"{session.duration_minutes} min"
            room = session.room.name if session.room else "TBD"

            print(f"  {session.session_id:<5} {trainer_name:<20} {date_time:<20} {duration:<10} {room:<10}")

        print("  " + "-" * 80)
        input("\nPress Enter to continue...")

    def book_pt_session(self):
        """Book a new personal training session."""
        self.print_header("BOOK PERSONAL TRAINING SESSION")

        # Show available trainers
        trainers = self.member_service.get_available_trainers()
        if not trainers:
            print("\n  No trainers available.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available Trainers:\n")
        for trainer in trainers:
            print(f"    [{trainer.trainer_id}] {trainer.first_name} {trainer.last_name}")
            if trainer.specialization:
                print(f"         Specialization: {trainer.specialization}")

        trainer_id = input("\n  Enter Trainer ID: ").strip()
        try:
            trainer_id = int(trainer_id)
        except ValueError:
            print("  Invalid trainer ID.")
            input("\nPress Enter to continue...")
            return

        # Get session date and time
        date_str = input("  Session date (YYYY-MM-DD): ").strip()
        time_str = input("  Session time (HH:MM, 24h format): ").strip()

        try:
            scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            print("  Invalid date or time format.")
            input("\nPress Enter to continue...")
            return

        # Get duration
        duration_str = input("  Duration in minutes (default 60): ").strip()
        duration = int(duration_str) if duration_str else 60

        # Optional notes
        notes = input("  Session notes (optional): ").strip() or None

        # Book the session
        result = self.member_service.book_personal_training_session(
            member_id=self.member.member_id,
            trainer_id=trainer_id,
            scheduled_time=scheduled_time,
            duration_minutes=duration,
            notes=notes
        )

        if result['success']:
            print("\n  ✓ Personal training session booked successfully!")
            print(f"  Session ID: {result['session_id']}")
        else:
            print(f"\n  ✗ Error: {result['error']}")

        input("\nPress Enter to continue...")

    def cancel_pt_session(self):
        """Cancel a personal training session."""
        self.print_header("CANCEL PT SESSION")

        sessions = self.member_service.get_member_pt_sessions(self.member.member_id)

        if not sessions:
            print("\n  No upcoming sessions to cancel.")
            input("\nPress Enter to continue...")
            return

        print("\n  Your upcoming sessions:")
        for session in sessions:
            trainer = session.trainer
            print(f"    [{session.session_id}] {trainer.first_name} {trainer.last_name} - "
                  f"{session.scheduled_time.strftime('%Y-%m-%d %H:%M')}")

        session_id = input("\n  Enter Session ID to cancel: ").strip()
        try:
            session_id = int(session_id)
        except ValueError:
            print("  Invalid session ID.")
            input("\nPress Enter to continue...")
            return

        confirm = input("  Are you sure you want to cancel this session? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Cancelled.")
            input("\nPress Enter to continue...")
            return

        result = self.member_service.cancel_pt_session(self.member.member_id, session_id)

        if result['success']:
            print("\n  ✓ Session cancelled successfully!")
        else:
            print(f"\n  ✗ Error: {result['error']}")

        input("\nPress Enter to continue...")

    # ==================== Group Class Registration ====================

    def manage_class_registrations(self):
        """Group class registration management submenu."""
        while True:
            self.print_header("GROUP CLASS REGISTRATION")

            options = [
                "View Available Classes",
                "Register for a Class",
                "View My Class Registrations",
                "Cancel Class Registration",
                "Back to Main Menu"
            ]
            self.print_menu(options)

            choice = input("Select option (1-5): ").strip()

            if choice == '1':
                self.view_available_classes()
            elif choice == '2':
                self.register_for_class()
            elif choice == '3':
                self.view_my_class_registrations()
            elif choice == '4':
                self.cancel_class_registration()
            elif choice == '5':
                break
            else:
                print("Invalid choice.")

    def view_available_classes(self):
        """View available fitness classes."""
        self.print_header("AVAILABLE FITNESS CLASSES")

        classes = self.member_service.get_available_classes()

        if not classes:
            print("\n  No upcoming classes available.")
            input("\nPress Enter to continue...")
            return

        print(f"\n  {len(classes)} upcoming class(es):\n")
        print("  " + "-" * 100)
        print(f"  {'ID':<5} {'Name':<25} {'Trainer':<20} {'Date/Time':<20} {'Capacity':<12}")
        print("  " + "-" * 100)

        for cls in classes:
            trainer = cls.trainer
            trainer_name = f"{trainer.first_name} {trainer.last_name}"
            date_time = cls.scheduled_time.strftime("%Y-%m-%d %H:%M")

            # Get current registration count
            from models import ClassRegistration, RegistrationStatus
            registered = self.session.query(ClassRegistration).filter(
                ClassRegistration.class_id == cls.class_id,
                ClassRegistration.status == RegistrationStatus.REGISTERED
            ).count()

            capacity_str = f"{registered}/{cls.capacity}"

            print(f"  {cls.class_id:<5} {cls.name:<25} {trainer_name:<20} {date_time:<20} {capacity_str:<12}")

        print("  " + "-" * 100)
        input("\nPress Enter to continue...")

    def register_for_class(self):
        """Register for a fitness class."""
        self.print_header("REGISTER FOR CLASS")

        classes = self.member_service.get_available_classes()

        if not classes:
            print("\n  No classes available for registration.")
            input("\nPress Enter to continue...")
            return

        # Show available classes
        print("\n  Available Classes:\n")
        for cls in classes:
            trainer = cls.trainer
            print(f"    [{cls.class_id}] {cls.name}")
            print(f"         Trainer: {trainer.first_name} {trainer.last_name}")
            print(f"         Time: {cls.scheduled_time.strftime('%Y-%m-%d %H:%M')} ({cls.duration_minutes} min)")
            print(f"         Capacity: {cls.capacity}")
            if cls.description:
                print(f"         Description: {cls.description}")
            print()

        class_id = input("  Enter Class ID to register: ").strip()
        try:
            class_id = int(class_id)
        except ValueError:
            print("  Invalid class ID.")
            input("\nPress Enter to continue...")
            return

        # Register for the class
        result = self.member_service.register_for_class(self.member.member_id, class_id)

        if result['success']:
            print("\n  ✓ Successfully registered for the class!")
        else:
            print(f"\n  ✗ Error: {result['error']}")

        input("\nPress Enter to continue...")

    def view_my_class_registrations(self):
        """View member's class registrations."""
        self.print_header("MY CLASS REGISTRATIONS")

        registrations = self.member_service.get_member_class_registrations(self.member.member_id)

        if not registrations:
            print("\n  You have no upcoming class registrations.")
            input("\nPress Enter to continue...")
            return

        print(f"\n  You are registered for {len(registrations)} class(es):\n")
        print("  " + "-" * 90)
        print(f"  {'Reg ID':<8} {'Class Name':<25} {'Trainer':<20} {'Date/Time':<20}")
        print("  " + "-" * 90)

        for reg in registrations:
            cls = reg.fitness_class
            trainer = cls.trainer
            trainer_name = f"{trainer.first_name} {trainer.last_name}"
            date_time = cls.scheduled_time.strftime("%Y-%m-%d %H:%M")

            print(f"  {reg.registration_id:<8} {cls.name:<25} {trainer_name:<20} {date_time:<20}")

        print("  " + "-" * 90)
        input("\nPress Enter to continue...")

    def cancel_class_registration(self):
        """Cancel a class registration."""
        self.print_header("CANCEL CLASS REGISTRATION")

        registrations = self.member_service.get_member_class_registrations(self.member.member_id)

        if not registrations:
            print("\n  You have no registrations to cancel.")
            input("\nPress Enter to continue...")
            return

        print("\n  Your class registrations:")
        for reg in registrations:
            cls = reg.fitness_class
            print(f"    [{reg.registration_id}] {cls.name} - {cls.scheduled_time.strftime('%Y-%m-%d %H:%M')}")

        reg_id = input("\n  Enter Registration ID to cancel: ").strip()
        try:
            reg_id = int(reg_id)
        except ValueError:
            print("  Invalid registration ID.")
            input("\nPress Enter to continue...")
            return

        confirm = input("  Are you sure you want to cancel this registration? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Cancelled.")
            input("\nPress Enter to continue...")
            return

        result = self.member_service.cancel_class_registration(self.member.member_id, reg_id)

        if result['success']:
            print("\n  ✓ Registration cancelled successfully!")
        else:
            print(f"\n  ✗ Error: {result['error']}")

        input("\nPress Enter to continue...")
