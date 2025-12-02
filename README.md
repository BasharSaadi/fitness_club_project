# Health and Fitness Club Management System

**COMP 3005 - Fall 2025 Final Project**

A database-driven management system for a modern fitness center, supporting members, trainers, and administrative staff with role-based access and comprehensive functionality.

## Author

Bashar Saadi
COMP 3005 - Fall 2025

## Technology Stack

- **Language:** Python 3.10+
- **Database:** PostgreSQL 14+
- **ORM:** SQLAlchemy 2.0
- **Interface:** Command-Line Interface (CLI)

## Project Structure

```
/project-root
├── /models          # ORM entity classes
│   ├── base.py      # Database connection & session
│   ├── member.py    # Member entity
│   ├── trainer.py   # Trainer entity
│   ├── admin.py     # Admin entity
│   ├── room.py      # Room entity
│   ├── health_metric.py
│   ├── fitness_goal.py
│   ├── trainer_availability.py
│   ├── fitness_class.py
│   ├── personal_training_session.py
│   ├── room_booking.py
│   └── class_registration.py
├── /services        # Business logic layer
│   ├── member_service.py
│   ├── trainer_service.py
│   └── admin_service.py
├── /app             # CLI application
│   ├── main.py      # Entry point
│   ├── cli.py       # Main controller
│   ├── member_cli.py
│   ├── trainer_cli.py
│   └── admin_cli.py
├── /scripts         # Utility scripts
│   ├── seed_data.py
│   └── advanced_sql_features.sql
├── /docs            # Documentation
│   └── ERD.pdf
├── config.py        # Configuration
├── requirements.txt # Dependencies
└── README.md
```

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

### 2. Configuration

Edit `config.py` or create a `.env` file:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fitness_club
DB_USER=postgres
DB_PASSWORD=your_password
```

### 3. Initialize and Seed Database

```bash
pip install -r requirements.txt

# Seed with sample data
python scripts/seed_data.py

# Apply advanced SQL features (view, trigger, indexes)
psql -U postgres -d fitness_club -f scripts/advanced_sql_features.sql
```

### 6. Run the Application

```bash
python app/main.py
```

## Sample Login Credentials

| Role    | Email                     | Password   |
| ------- | ------------------------- | ---------- |
| Member  | alice@email.com           | member123  |
| Trainer | john.yoga@fitnessclub.com | trainer123 |
| Admin   | admin@fitnessclub.com     | admin123   |

## Implemented Features (10 Operations)

### Member Functions (6)

1. **User Registration** - Create account with unique email
2. **Profile Management** - Update personal details and goals
3. **Health Metrics Logging** - Record metrics with history preservation
4. **Dashboard** - View summary of health, goals, and activity
5. **PT Session Booking** - Book/cancel personal training sessions with availability & conflict validation
6. **Group Class Registration** - Register for classes with capacity checks and conflict detection

### Trainer Functions (2)

7. **Set Availability** - Define time slots with overlap prevention
8. **Member Lookup** - Search and view member info (read-only)

### Admin Functions (2)

9. **Room Booking** - Reserve rooms with double-booking prevention
10. **Class Management** - Create/update/cancel fitness classes

## Database Features

- **View:** `member_dashboard_view` - Aggregated member data
- **Trigger:** `trg_update_goal_on_metric` - Auto-updates goals on health metric entry
- **Indexes:** Optimized queries on email, availability, and bookings

## ORM Usage

This project uses SQLAlchemy ORM throughout:

- All entities defined as Python classes with relationships
- No raw SQL in application code
- Automatic schema creation from models
- Proper handling of one-to-many and many-to-many relationships

## Documentation

- **ERD:** [docs/ERD.pdf](docs/ERD.pdf) - Entity-Relationship Diagram
- **Normalization:** [docs/NORMALIZATION.md](docs/NORMALIZATION.md) - Complete 2NF/3NF analysis with proofs
- **SQL Features:** [scripts/advanced_sql_features.sql](scripts/advanced_sql_features.sql) - View, trigger, and indexes

