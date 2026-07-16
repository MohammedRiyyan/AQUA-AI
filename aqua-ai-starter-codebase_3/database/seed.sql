-- Global container presets (user_id IS NULL) and the achievement catalog.
-- Run after schema.sql: psql -U aqua -d aqua_ai -f database/seed.sql

INSERT INTO containers (name, capacity_ml, icon, color) VALUES
    ('Small Glass', 150, 'glass', '#17D3FF'),
    ('Glass', 200, 'glass', '#17D3FF'),
    ('Large Glass', 250, 'glass', '#17D3FF'),
    ('Tall Glass', 300, 'glass', '#17D3FF'),
    ('Big Glass', 350, 'glass', '#17D3FF'),
    ('XL Glass', 400, 'glass', '#17D3FF'),
    ('Mug', 500, 'mug', '#0BA5A0'),
    ('Small Bottle', 500, 'bottle', '#3A6FF7'),
    ('Standard Bottle', 750, 'bottle', '#3A6FF7'),
    ('1L Bottle', 1000, 'bottle', '#3A6FF7'),
    ('1.5L Bottle', 1500, 'bottle', '#3A6FF7'),
    ('2L Bottle', 2000, 'bottle', '#3A6FF7');

INSERT INTO achievements (key, name, description, icon, criteria) VALUES
    ('seven_day_streak', '7 Day Streak', 'Hit your hydration goal 7 days in a row.', 'flame', 'current_streak_days >= 7'),
    ('hydration_master', 'Hydration Master', 'Hit your hydration goal 30 days in a row.', 'droplet', 'current_streak_days >= 30'),
    ('ocean_level', 'Ocean Level', 'Logged 50 liters of water in total.', 'waves', 'lifetime_total_ml >= 50000'),
    ('aqua_legend', 'Aqua Legend', 'Hit your hydration goal 100 days in a row.', 'star', 'current_streak_days >= 100'),
    ('100l_club', '100L Club', 'Logged 100 liters of water in total.', 'trophy', 'lifetime_total_ml >= 100000'),
    ('500l_club', '500L Club', 'Logged 500 liters of water in total.', 'crown', 'lifetime_total_ml >= 500000');
