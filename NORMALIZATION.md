# Database Normalization Analysis

**Health and Fitness Club Management System**
**Author:** Bashar Saadi
**Course:** COMP 3005 - Fall 2025

---

## Table of Contents

1. [Functional Dependencies](#functional-dependencies)
2. [First Normal Form (1NF)](#first-normal-form-1nf)
3. [Second Normal Form (2NF)](#second-normal-form-2nf)
4. [Third Normal Form (3NF)](#third-normal-form-3nf)
5. [Conclusion](#conclusion)

---

## Functional Dependencies

Below are the key functional dependencies identified in our schema:

### Members Table

- `member_id → email, password_hash, first_name, last_name, date_of_birth, gender, phone, created_at`
- Primary Key: `member_id`

### Trainers Table

- `trainer_id → email, password_hash, first_name, last_name, specialization, phone, created_at`
- Primary Key: `trainer_id`

### Admins Table

- `admin_id → email, password_hash, first_name, last_name, created_at`
- Primary Key: `admin_id`

### Rooms Table

- `room_id → name, capacity, room_type, created_at`
- Primary Key: `room_id`

### Health_Metrics Table

- `metric_id → member_id, recorded_at, weight_kg, height_cm, body_fat_percentage, resting_heart_rate`
- Primary Key: `metric_id`
- Foreign Key: `member_id → members.member_id`

### Fitness_Goals Table

- `goal_id → member_id, goal_type, target_value, current_value, target_date, status, created_at`
- Primary Key: `goal_id`
- Foreign Key: `member_id → members.member_id`

### Trainer_Availability Table

- `availability_id → trainer_id, day_of_week, start_time, end_time`
- Primary Key: `availability_id`
- Foreign Key: `trainer_id → trainers.trainer_id`

### Fitness_Classes Table

- `class_id → name, description, trainer_id, room_id, scheduled_time, duration_minutes, capacity, status, created_at`
- Primary Key: `class_id`
- Foreign Keys:
  - `trainer_id → trainers.trainer_id`
  - `room_id → rooms.room_id`

### Personal_Training_Sessions Table

- `session_id → member_id, trainer_id, room_id, scheduled_time, duration_minutes, status, created_at`
- Primary Key: `session_id`
- Foreign Keys:
  - `member_id → members.member_id`
  - `trainer_id → trainers.trainer_id`
  - `room_id → rooms.room_id`

### Room_Bookings Table

- `booking_id → room_id, booking_date, start_time, end_time, purpose, status, created_at`
- Primary Key: `booking_id`
- Foreign Key: `room_id → rooms.room_id`

### Class_Registrations Table (Junction Table)

- `registration_id → member_id, class_id, registered_at, status`
- Primary Key: `registration_id`
- Foreign Keys:
  - `member_id → members.member_id`
  - `class_id → fitness_classes.class_id`

---

## First Normal Form (1NF)

**Definition:** A table is in 1NF if:

1. All attributes contain only atomic (indivisible) values
2. Each column contains values of a single type
3. Each row is unique (has a primary key)
4. No repeating groups or arrays

### Analysis

**All tables satisfy 1NF:**

1. **Members Table:**

   - All attributes are atomic (email, first_name, last_name are single strings)
   - Primary key: `member_id`
   - No multi-valued attributes
2. **Trainers Table:**

   - `specialization` stores text but is treated as a single field (could be normalized further but acceptable)
   - All other attributes atomic
   - Primary key: `trainer_id`
3. **Health_Metrics Table:**

   - Each metric (weight, height, body_fat, heart_rate) is atomic
   - Each row represents a single metric recording at a point in time
   - Primary key: `metric_id`
4. **Fitness_Goals Table:**

   - Goal type, target, current value are all atomic
   - Primary key: `goal_id`
5. **Fitness_Classes Table:**

   - All attributes atomic (name, description, capacity, etc.)
   - Primary key: `class_id`
6. **Class_Registrations Table:**

   - Junction table with atomic attributes
   - Primary key: `registration_id`
7. **All other tables** follow 1NF with atomic values and proper primary keys.

**Conclusion:** All tables are in 1NF.

---

## Second Normal Form (2NF)

**Definition:** A table is in 2NF if:

1. It is in 1NF
2. All non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies)

**Note:** Partial dependencies only occur in tables with composite primary keys.

### Analysis

**All tables satisfy 2NF:**

**Tables with Single-Column Primary Keys:**

- `members` (PK: `member_id`)
- `trainers` (PK: `trainer_id`)
- `admins` (PK: `admin_id`)
- `rooms` (PK: `room_id`)
- `health_metrics` (PK: `metric_id`)
- `fitness_goals` (PK: `goal_id`)
- `trainer_availability` (PK: `availability_id`)
- `fitness_classes` (PK: `class_id`)
- `personal_training_sessions` (PK: `session_id`)
- `room_bookings` (PK: `booking_id`)
- `class_registrations` (PK: `registration_id`)

**Reasoning:**

- Since all tables use single-column surrogate keys (auto-incrementing integers), partial dependencies **cannot exist**.
- Every non-key attribute depends on the entire primary key by definition.
- Foreign keys reference other tables appropriately without introducing partial dependencies.

**Example - Class_Registrations Table:**

- PK: `registration_id`
- Attributes: `member_id, class_id, registered_at, status`
- All attributes (`member_id`, `class_id`, `registered_at`, `status`) depend on the full primary key `registration_id`.
- No partial dependency exists.

**Alternative Design Consideration:**

- An alternative would be composite PK: `(member_id, class_id)`
- However, this would still be in 2NF because:
  - `registered_at` depends on the full key (when member registered for that specific class)
  - `status` depends on the full key (status of that specific registration)

**Conclusion:** All tables are in 2NF.

---

## Third Normal Form (3NF)

**Definition:** A table is in 3NF if:

1. It is in 2NF
2. No transitive dependencies exist (non-key attributes do not depend on other non-key attributes)

### Analysis

**All tables satisfy 3NF:**

### Members Table

- **Attributes:** `member_id, email, password_hash, first_name, last_name, date_of_birth, gender, phone, created_at`
- **Check for transitive dependencies:**
  - `first_name` does NOT determine `last_name` (many people share first names)
  - `email` does NOT determine other attributes (it's an alternate key, not a non-key attribute used transitively)
  - No attribute depends on another non-key attribute
- **Conclusion:** In 3NF

### Trainers Table

- **Attributes:** `trainer_id, email, password_hash, first_name, last_name, specialization, phone, created_at`
- **Check:** Same as members—no transitive dependencies
- **Conclusion:** In 3NF

### Health_Metrics Table

- **Attributes:** `metric_id, member_id, recorded_at, weight_kg, height_cm, body_fat_percentage, resting_heart_rate`
- **Check for transitive dependencies:**
  - `weight_kg` does NOT determine `height_cm` (independent measurements)
  - `body_fat_percentage` is independent
  - `resting_heart_rate` is independent
  - All metrics are measurements recorded at a point in time, not derived from each other
- **Conclusion:** In 3NF

### Fitness_Goals Table

- **Attributes:** `goal_id, member_id, goal_type, target_value, current_value, target_date, status, created_at`
- **Check for transitive dependencies:**
  - `goal_type` does NOT determine `target_value` (different members have different targets for the same goal type)
  - `current_value` does NOT determine `status` (status is updated via trigger based on comparison logic, not pure dependency)
  - `target_date` is independent
- **Conclusion:** In 3NF

### Fitness_Classes Table

- **Attributes:** `class_id, name, description, trainer_id, room_id, scheduled_time, duration_minutes, capacity, status, created_at`
- **Check for transitive dependencies:**
  - `trainer_id` does NOT determine `room_id` (trainers can use different rooms)
  - `name` does NOT determine `description` (same class name can have different descriptions)
  - `capacity` depends on `room_id` but is stored here for **denormalization for performance** (acceptable trade-off)
  - However, to strictly satisfy 3NF, capacity should ideally be retrieved from `rooms` table

**Design Decision:**

- Capacity is copied from the room at class creation time for historical accuracy (room capacity might change, but class capacity is fixed at creation)
- This is an intentional **controlled denormalization** for business logic, not a 3NF violation
- **Justification:** If room capacity changes after class is scheduled, the class should retain its original capacity

**Alternative Strict 3NF:**

- Store `capacity` only in `rooms` table
- Query `rooms.capacity` via join when needed
- **Trade-off:** Loses historical context if room capacity changes

**Conclusion:** In 3NF (with justified denormalization for business rules)

### Personal_Training_Sessions Table

- **Attributes:** `session_id, member_id, trainer_id, room_id, scheduled_time, duration_minutes, status, created_at`
- **Check:** No non-key attribute determines another
- **Conclusion:**  In 3NF

### Room_Bookings Table

- **Attributes:** `booking_id, room_id, booking_date, start_time, end_time, purpose, status, created_at`
- **Check:** `start_time` and `end_time` are independent; `purpose` does not determine other attributes
- **Conclusion:** In 3NF

### Class_Registrations Table

- **Attributes:** `registration_id, member_id, class_id, registered_at, status`
- **Check:** No transitive dependencies
- **Conclusion:** In 3NF

### Trainer_Availability Table

- **Attributes:** `availability_id, trainer_id, day_of_week, start_time, end_time`
- **Check:** Time slots are independent; no transitive dependencies
- **Conclusion:** In 3NF

---

## Proof of No Partial Dependencies (2NF)

Since all tables use **surrogate primary keys** (single-column auto-increment integers), partial dependencies are structurally impossible:

- **Partial Dependency** requires a composite key: `(A, B) → C` where `A → C` (C depends on only part of the key)
- With single-column primary keys, all non-key attributes must depend on the **entire** (and only) primary key
- Therefore, 2NF is **automatically satisfied**

---

## Proof of No Transitive Dependencies (3NF)

For each table, we verified that:

1. No non-key attribute determines another non-key attribute
2. All attributes are either:
   - Directly dependent on the primary key, OR
   - Foreign keys referencing other tables, OR
   - Independent measurements/values

**Example - Members Table:**

- `email → member_id` (reverse dependency, email is alternate key, not a transitive path)
- `first_name` and `last_name` are independent
- `date_of_birth`, `gender`, `phone` are independent facts about the member
- No transitive path exists: `member_id → X → Y`

**Example - Health_Metrics Table:**

- Each metric (weight, height, body_fat, heart_rate) is an independent measurement
- None determines another: `weight ↛ height`, `height ↛ body_fat`, etc.
- All depend directly on `metric_id`

---

## Conclusion

### Summary of Normalization Status

| Table                      | 1NF | 2NF | 3NF | Notes                                |
| -------------------------- | --- | --- | --- | ------------------------------------ |
| members                    | ✓  | ✓  | ✓  | Fully normalized                     |
| trainers                   | ✓  | ✓  | ✓  | Fully normalized                     |
| admins                     | ✓  | ✓  | ✓  | Fully normalized                     |
| rooms                      | ✓  | ✓  | ✓  | Fully normalized                     |
| health_metrics             | ✓  | ✓  | ✓  | Fully normalized, historical data    |
| fitness_goals              | ✓  | ✓  | ✓  | Fully normalized                     |
| trainer_availability       | ✓  | ✓  | ✓  | Fully normalized                     |
| fitness_classes            | ✓  | ✓  | ✓  | Justified denormalization (capacity) |
| personal_training_sessions | ✓  | ✓  | ✓  | Fully normalized                     |
| room_bookings              | ✓  | ✓  | ✓  | Fully normalized                     |
| class_registrations        | ✓  | ✓  | ✓  | Fully normalized, junction table     |

### Key Design Decisions

1. **Surrogate Keys:** All tables use auto-increment integer primary keys, ensuring 2NF automatically
2. **Historical Data:** Health metrics and goals support time-series tracking without overwriting
3. **Junction Tables:** Many-to-many relationships (members-classes) properly normalized with `class_registrations`
4. **Controlled Denormalization:** Class capacity copied from room for historical accuracy (business rule)
5. **No Redundancy:** All data stored once except for justified denormalization

### Verification

**No Partial Dependencies:**

- All tables use single-column primary keys

**No Transitive Dependencies:**

- All non-key attributes depend directly on primary key only
- No attribute determines another non-key attribute

**Result:** The database schema is fully normalized to **3NF** with all design decisions justified by business requirements.
