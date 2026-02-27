-- ===============================
-- Seed Data — Phase 3
-- Added ambulance user
-- ===============================

INSERT INTO public.hospitals (facility_id, name, city, latitude, longitude)
VALUES
    ('H001', 'Pune Central Hospital', 'Pune', 18.5204, 73.8567),
    ('H002', 'Mumbai General', 'Mumbai', 19.076, 72.8777),
    ('H003', 'Delhi Care Institute', 'Delhi', 28.7041, 77.1025),
    ('H004', 'Bangalore Medical Center', 'Bangalore', 12.9716, 77.5946)
ON CONFLICT (facility_id) DO NOTHING;

INSERT INTO public.hospital_capacity (facility_id, beds_total, ventilators_total, oxygen_sources_total)
VALUES
    ('H001', 10, 10, 4),
    ('H002', 10, 10, 4),
    ('H003', 10, 10, 4),
    ('H004', 10, 10, 4)
ON CONFLICT (facility_id) DO NOTHING;

INSERT INTO public.hospital_state (facility_id, beds_occupied, ventilators_in_use, oxygen_percent, oxygen_status)
VALUES
    ('H001', 0, 0, 100.0, 'NORMAL'),
    ('H002', 0, 0, 100.0, 'NORMAL'),
    ('H003', 0, 0, 100.0, 'NORMAL'),
    ('H004', 0, 0, 100.0, 'NORMAL')
ON CONFLICT (facility_id) DO NOTHING;

INSERT INTO public.users (username, password_hash, role, facility_id)
VALUES
    ('admin', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'admin', 'H001'),
    ('hospital1', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital', 'H001'),
    ('hospital2', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital', 'H002'),
    ('ambulance1', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'ambulance', NULL)
ON CONFLICT (username) DO NOTHING;
