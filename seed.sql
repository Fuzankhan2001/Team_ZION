-- ===============================
-- Seed Data — Phase 1
-- ===============================

INSERT INTO public.hospitals (facility_id, name, city, latitude, longitude)
VALUES
    ('H001', 'Pune Central Hospital', 'Pune', 18.5204, 73.8567),
    ('H002', 'Mumbai General', 'Mumbai', 19.076, 72.8777)
ON CONFLICT (facility_id) DO NOTHING;

-- password: admin123 (bcrypt hash)
INSERT INTO public.users (username, password_hash, role, facility_id)
VALUES
    ('admin', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'admin', 'H001')
ON CONFLICT (username) DO NOTHING;
