-- Advanced SQL Features for Health and Fitness Club Management System
-- This file contains: 1 View, 1 Trigger, and Database Indexes

-- ============================================================
-- DATABASE INDEXES
-- ============================================================

-- Index on member email for fast login lookups
CREATE INDEX IF NOT EXISTS idx_member_email ON members(email);

-- Index on trainer availability for schedule lookups
CREATE INDEX IF NOT EXISTS idx_trainer_availability_lookup 
ON trainer_availability(trainer_id, day_of_week);

-- Index on health metrics for member history queries
CREATE INDEX IF NOT EXISTS idx_health_metrics_member_date 
ON health_metrics(member_id, recorded_at DESC);

-- Index on fitness classes for schedule queries
CREATE INDEX IF NOT EXISTS idx_fitness_classes_schedule 
ON fitness_classes(scheduled_time, status);

-- Index on room bookings for availability checks
CREATE INDEX IF NOT EXISTS idx_room_bookings_availability 
ON room_bookings(room_id, booking_date, status);

-- ============================================================
-- DATABASE VIEW: member_dashboard_view
-- ============================================================
-- This view aggregates member data for the dashboard feature,
-- providing a single query to retrieve member summary information.

CREATE OR REPLACE VIEW member_dashboard_view AS
SELECT 
    m.member_id,
    m.email,
    m.first_name,
    m.last_name,
    m.created_at AS member_since,
    
    -- Latest health metric (subquery for most recent)
    (SELECT hm.weight_kg 
     FROM health_metrics hm 
     WHERE hm.member_id = m.member_id 
     ORDER BY hm.recorded_at DESC 
     LIMIT 1) AS latest_weight_kg,
    
    (SELECT hm.height_cm 
     FROM health_metrics hm 
     WHERE hm.member_id = m.member_id 
     ORDER BY hm.recorded_at DESC 
     LIMIT 1) AS latest_height_cm,
    
    (SELECT hm.body_fat_percentage 
     FROM health_metrics hm 
     WHERE hm.member_id = m.member_id 
     ORDER BY hm.recorded_at DESC 
     LIMIT 1) AS latest_body_fat,
    
    (SELECT hm.recorded_at 
     FROM health_metrics hm 
     WHERE hm.member_id = m.member_id 
     ORDER BY hm.recorded_at DESC 
     LIMIT 1) AS last_metric_date,
    
    -- Count of health metric entries
    (SELECT COUNT(*) 
     FROM health_metrics hm 
     WHERE hm.member_id = m.member_id) AS total_metric_entries,
    
    -- Active goal information
    (SELECT fg.goal_type 
     FROM fitness_goals fg 
     WHERE fg.member_id = m.member_id 
     AND fg.status = 'active' 
     ORDER BY fg.created_at DESC 
     LIMIT 1) AS active_goal_type,
    
    (SELECT fg.target_value 
     FROM fitness_goals fg 
     WHERE fg.member_id = m.member_id 
     AND fg.status = 'active' 
     ORDER BY fg.created_at DESC 
     LIMIT 1) AS active_goal_target,
    
    -- Count of active goals
    (SELECT COUNT(*) 
     FROM fitness_goals fg 
     WHERE fg.member_id = m.member_id 
     AND fg.status = 'active') AS active_goals_count,
    
    -- Count of class registrations
    (SELECT COUNT(*) 
     FROM class_registrations cr 
     WHERE cr.member_id = m.member_id) AS total_class_registrations,
    
    -- Count of attended classes
    (SELECT COUNT(*) 
     FROM class_registrations cr 
     WHERE cr.member_id = m.member_id 
     AND cr.status = 'attended') AS classes_attended

FROM members m;

-- Grant usage comment for documentation
COMMENT ON VIEW member_dashboard_view IS 
'Aggregated view for member dashboard. Provides summary of health metrics, goals, and class participation.';


-- ============================================================
-- DATABASE TRIGGER: update_goal_on_health_metric
-- ============================================================
-- This trigger automatically updates weight-related fitness goals
-- when a new health metric is logged, checking if the goal has been achieved.

-- First, create the trigger function
CREATE OR REPLACE FUNCTION update_goal_on_health_metric()
RETURNS TRIGGER AS $$
BEGIN
    -- Update weight_loss goals when weight metric is logged
    IF NEW.weight_kg IS NOT NULL THEN
        UPDATE fitness_goals 
        SET 
            current_value = NEW.weight_kg,
            status = CASE 
                WHEN goal_type = 'weight_loss' AND NEW.weight_kg <= target_value THEN 'completed'
                WHEN goal_type = 'weight_gain' AND NEW.weight_kg >= target_value THEN 'completed'
                ELSE status 
            END
        WHERE member_id = NEW.member_id 
        AND goal_type IN ('weight_loss', 'weight_gain')
        AND status = 'active';
    END IF;
    
    -- Update body_fat_reduction goals when body fat percentage is logged
    IF NEW.body_fat_percentage IS NOT NULL THEN
        UPDATE fitness_goals 
        SET 
            current_value = NEW.body_fat_percentage,
            status = CASE 
                WHEN NEW.body_fat_percentage <= target_value THEN 'completed'
                ELSE status 
            END
        WHERE member_id = NEW.member_id 
        AND goal_type = 'body_fat_reduction'
        AND status = 'active';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger (drop first if exists to allow re-running)
DROP TRIGGER IF EXISTS trg_update_goal_on_metric ON health_metrics;

CREATE TRIGGER trg_update_goal_on_metric
AFTER INSERT ON health_metrics
FOR EACH ROW
EXECUTE FUNCTION update_goal_on_health_metric();

-- Add comment for documentation
COMMENT ON FUNCTION update_goal_on_health_metric() IS 
'Automatically updates fitness goals when health metrics are logged. Marks goals as completed when targets are reached.';


-- ============================================================
-- VERIFICATION QUERIES (for testing)
-- ============================================================

-- Test view (uncomment to test)
-- SELECT * FROM member_dashboard_view;

-- Test that trigger function exists
-- SELECT proname FROM pg_proc WHERE proname = 'update_goal_on_health_metric';

-- Test that indexes exist
-- SELECT indexname FROM pg_indexes WHERE tablename = 'members';
