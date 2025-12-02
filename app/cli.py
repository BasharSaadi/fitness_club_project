import sys
from models import get_session, init_db
from services import MemberService, TrainerService, AdminService
from app.member_cli import MemberCLI
from app.trainer_cli import TrainerCLI
from app.admin_cli import AdminCLI


class FitnessClubCLI:
    """Main CLI controller for the fitness club system."""

    def __init__(self):
        self.session = None
        self.current_user = None
        self.current_role = None

    def clear_screen(self):
        """Clear the terminal screen."""
        print("\n" * 2)

    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_menu(self, options: list):
        """Print a numbered menu."""
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print()

    def get_choice(self, prompt: str = "Enter choice: ", valid_range: range = None) -> str:
        """Get user input with optional validation."""
        while True:
            try:
                choice = input(prompt).strip()
                if valid_range and choice.isdigit():
                    if int(choice) not in valid_range:
                        print(f"Please enter a number between {valid_range.start} and {valid_range.stop - 1}")
                        continue
                return choice
            except KeyboardInterrupt:
                print("\n\nExiting...")
                sys.exit(0)

    def initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            print("\nInitializing database...")
            self.session = get_session()
            init_db()
            print("Database initialized successfully!")
            return True
        except Exception as e:
            print(f"\nError connecting to database: {e}")
            print("\nPlease ensure PostgreSQL is running and the database 'fitness_club' exists.")
            print("You can create it with: createdb fitness_club")
            return False

    def run(self):
        """Main application loop."""
        self.print_header("HEALTH AND FITNESS CLUB MANAGEMENT SYSTEM")
        print("\nWelcome to the Health and Fitness Club Management System!")
        
        if not self.initialize_database():
            print("\nFailed to connect to database. Exiting.")
            sys.exit(1)

        try:
            while True:
                self.main_menu()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
        finally:
            if self.session:
                self.session.close()

    def main_menu(self):
        """Display main menu and handle role selection."""
        self.print_header("MAIN MENU")
        
        options = [
            "Member Login/Register",
            "Trainer Login/Register",
            "Admin Login/Register",
            "Exit"
        ]
        self.print_menu(options)
        
        choice = self.get_choice("Select your role (1-4): ", range(1, 5))
        
        if choice == '1':
            self.member_menu()
        elif choice == '2':
            self.trainer_menu()
        elif choice == '3':
            self.admin_menu()
        elif choice == '4':
            print("\nThank you for using the Fitness Club System. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

    def member_menu(self):
        """Handle member authentication and operations."""
        self.print_header("MEMBER ACCESS")
        
        options = [
            "Login",
            "Register New Account",
            "Back to Main Menu"
        ]
        self.print_menu(options)
        
        choice = self.get_choice("Select option (1-3): ", range(1, 4))
        
        member_service = MemberService(self.session)
        
        if choice == '1':
            # Login
            print("\n--- Member Login ---")
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            
            result = member_service.authenticate_member(email, password)
            if result['success']:
                self.current_user = result['data']
                self.current_role = 'member'
                print(f"\nWelcome back, {self.current_user.first_name}!")
                
                # Enter member CLI
                member_cli = MemberCLI(self.session, self.current_user)
                member_cli.run()
            else:
                print(f"\nLogin failed: {result['error']}")
                
        elif choice == '2':
            # Register
            print("\n--- New Member Registration ---")
            email = input("Email: ").strip()
            password = input("Password (min 8 chars): ").strip()
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            phone = input("Phone (optional): ").strip() or None
            
            result = member_service.register_member(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            if result['success']:
                print(f"\nRegistration successful! Welcome, {first_name}!")
                print("Please login with your credentials.")
            else:
                print(f"\nRegistration failed: {result['error']}")

    def trainer_menu(self):
        """Handle trainer authentication and operations."""
        self.print_header("TRAINER ACCESS")
        
        options = [
            "Login",
            "Register New Account",
            "Back to Main Menu"
        ]
        self.print_menu(options)
        
        choice = self.get_choice("Select option (1-3): ", range(1, 4))
        
        trainer_service = TrainerService(self.session)
        
        if choice == '1':
            # Login
            print("\n--- Trainer Login ---")
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            
            result = trainer_service.authenticate_trainer(email, password)
            if result['success']:
                self.current_user = result['data']
                self.current_role = 'trainer'
                print(f"\nWelcome back, {self.current_user.first_name}!")
                
                # Enter trainer CLI
                trainer_cli = TrainerCLI(self.session, self.current_user)
                trainer_cli.run()
            else:
                print(f"\nLogin failed: {result['error']}")
                
        elif choice == '2':
            # Register
            print("\n--- New Trainer Registration ---")
            email = input("Email: ").strip()
            password = input("Password (min 8 chars): ").strip()
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            specialization = input("Specialization (e.g., Yoga, Strength): ").strip() or None
            phone = input("Phone (optional): ").strip() or None
            
            result = trainer_service.register_trainer(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                specialization=specialization,
                phone=phone
            )
            
            if result['success']:
                print(f"\nRegistration successful! Welcome, {first_name}!")
                print("Please login with your credentials.")
            else:
                print(f"\nRegistration failed: {result['error']}")

    def admin_menu(self):
        """Handle admin authentication and operations."""
        self.print_header("ADMIN ACCESS")
        
        options = [
            "Login",
            "Register New Account",
            "Back to Main Menu"
        ]
        self.print_menu(options)
        
        choice = self.get_choice("Select option (1-3): ", range(1, 4))
        
        admin_service = AdminService(self.session)
        
        if choice == '1':
            # Login
            print("\n--- Admin Login ---")
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            
            result = admin_service.authenticate_admin(email, password)
            if result['success']:
                self.current_user = result['data']
                self.current_role = 'admin'
                print(f"\nWelcome back, {self.current_user.first_name}!")
                
                # Enter admin CLI
                admin_cli = AdminCLI(self.session, self.current_user)
                admin_cli.run()
            else:
                print(f"\nLogin failed: {result['error']}")
                
        elif choice == '2':
            # Register
            print("\n--- New Admin Registration ---")
            email = input("Email: ").strip()
            password = input("Password (min 8 chars): ").strip()
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            
            result = admin_service.register_admin(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            if result['success']:
                print(f"\nRegistration successful! Welcome, {first_name}!")
                print("Please login with your credentials.")
            else:
                print(f"\nRegistration failed: {result['error']}")
