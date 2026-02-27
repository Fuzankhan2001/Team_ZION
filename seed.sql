-- ===============================
-- AIRA-Med Seed Data (matches live schema)
-- 8 hospitals, 5 cities, realistic load states
-- All passwords = "password123"
-- hash: $2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456
-- ===============================

-- ─── HOSPITALS ──────────────────────────────────────────────────────────────
INSERT INTO public.hospitals (facility_id, name, city, latitude, longitude)
VALUES
    ('H001', 'Pune Central Hospital',     'Pune',      18.5204,  73.8567),
    ('H002', 'Mumbai General',            'Mumbai',    19.0760,  72.8777),
    ('H003', 'Delhi Care Institute',      'Delhi',     28.7041,  77.1025),
    ('H004', 'Bangalore Medical Center',  'Bangalore', 12.9716,  77.5946),
    ('H005', 'Hyderabad Apollo Hub',      'Hyderabad', 17.3850,  78.4867),
    ('H006', 'Chennai Lifeline Hospital', 'Chennai',   13.0827,  80.2707),
    ('H007', 'Kolkata Metro Medical',     'Kolkata',   22.5726,  88.3639),
    ('H008', 'Pune North Trauma Center',  'Pune',      18.5642,  73.7769)
ON CONFLICT (facility_id) DO NOTHING;


-- ─── CAPACITY (no oxygen_sources_total in live schema) ───────────────────────
INSERT INTO public.hospital_capacity (facility_id, beds_total, ventilators_total)
VALUES
    ('H001', 120, 20),
    ('H002', 200, 35),
    ('H003', 180, 30),
    ('H004', 150, 25),
    ('H005', 100, 18),
    ('H006', 130, 22),
    ('H007', 160, 28),
    ('H008',  80, 12)
ON CONFLICT (facility_id) DO NOTHING;


-- ─── LIVE STATE (varied load levels for realistic demo dashboard) ────────────
-- UPSERT so re-running updates current state too
INSERT INTO public.hospital_state (facility_id, beds_occupied, ventilators_in_use, oxygen_percent, oxygen_status)
VALUES
    ('H001',  96, 17, 45.0, 'WARNING'),   -- near-critical beds, low oxygen
    ('H002',  80, 14, 88.0, 'NORMAL'),    -- high load, stable
    ('H003',  50, 10, 95.0, 'NORMAL'),    -- moderate load
    ('H004', 142, 24, 22.0, 'CRITICAL'),  -- crisis: beds AND oxygen critical
    ('H005',  30,  5, 98.0, 'NORMAL'),    -- light load, best referral candidate
    ('H006',  65, 11, 78.0, 'NORMAL'),    -- moderate
    ('H007', 155, 26, 35.0, 'WARNING'),   -- near full, oxygen warning
    ('H008',  10,  2, 99.0, 'NORMAL')     -- lightly used, great for referral
ON CONFLICT (facility_id) DO UPDATE SET
    beds_occupied      = EXCLUDED.beds_occupied,
    ventilators_in_use = EXCLUDED.ventilators_in_use,
    oxygen_percent     = EXCLUDED.oxygen_percent,
    oxygen_status      = EXCLUDED.oxygen_status,
    last_updated       = now();


-- ─── USERS ──────────────────────────────────────────────────────────────────
-- hospital  →  /hospital dashboard  (scoped to their own facility)
-- ambulance →  /ambulance dashboard (request referrals)
-- commander →  /commander dashboard (city-wide overview)
-- admin     →  /commander dashboard
INSERT INTO public.users (username, password_hash, role, facility_id)
VALUES
    ('admin',      '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'admin',     'H001'),
    ('hospital1',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H001'),
    ('hospital2',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H002'),
    ('hospital3',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H003'),
    ('hospital4',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H004'),
    ('hospital5',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H005'),
    ('hospital6',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H006'),
    ('hospital7',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H007'),
    ('hospital8',  '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'hospital',  'H008'),
    ('ambulance1', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'ambulance', NULL),
    ('ambulance2', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'ambulance', NULL),
    ('ambulance3', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'ambulance', NULL),
    ('commander1', '$2b$12$LJ3m4ys3Lk0TSwHjmO0pFeEBkVwI/x.Ue4RJc8bSsHnIvqOqBN456', 'commander', NULL)
ON CONFLICT (username) DO NOTHING;


-- ─── SAMPLE REFERRAL LOG ENTRIES ────────────────────────────────────────────
INSERT INTO public.referral_log
    (origin, destination_facility_id, patient_severity, recommended_by, decision_timestamp)
VALUES
    ('AMB-01', 'H008', 'CRITICAL', 'referral_agent', now() - interval '1 hour'),
    ('AMB-02', 'H001', 'SEVERE',   'referral_agent', now() - interval '30 min'),
    ('AMB-03', 'H005', 'MODERATE', 'referral_agent', now() - interval '10 min');
