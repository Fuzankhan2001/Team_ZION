-- ===============================
-- AIRA-Med Database Schema
-- Phase 3: Messaging + referral tables
-- ===============================

CREATE TABLE IF NOT EXISTS public.hospitals (
    facility_id text PRIMARY KEY,
    name text NOT NULL,
    city text NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.hospital_capacity (
    facility_id text PRIMARY KEY,
    beds_total integer NOT NULL,
    ventilators_total integer NOT NULL,
    oxygen_sources_total integer NOT NULL
);

CREATE TABLE IF NOT EXISTS public.hospital_state (
    facility_id text PRIMARY KEY,
    beds_occupied integer DEFAULT 0,
    ventilators_in_use integer DEFAULT 0,
    oxygen_percent double precision DEFAULT 100.0,
    oxygen_status text DEFAULT 'NORMAL',
    last_updated timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.hospital_state_audit (
    id serial PRIMARY KEY,
    facility_id text NOT NULL,
    delta jsonb NOT NULL,
    applied_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.hospital_history (
    id serial PRIMARY KEY,
    facility_id text NOT NULL,
    beds_occupied integer,
    oxygen_percent double precision,
    recorded_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.hospital_resources (
    facility_id text NOT NULL,
    resource_type text NOT NULL,
    resource_id text NOT NULL,
    current_value double precision,
    updated_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (facility_id, resource_type, resource_id)
);

CREATE TABLE IF NOT EXISTS public.hospital_network_messages (
    id serial PRIMARY KEY,
    sender_id varchar(50) NOT NULL,
    sender_name varchar(100) NOT NULL,
    message_text text NOT NULL,
    message_type varchar(20) DEFAULT 'CHAT',
    created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.incoming_admissions (
    id serial PRIMARY KEY,
    ambulance_id varchar(50),
    hospital_id varchar(50),
    patient_id varchar(50),
    severity varchar(20),
    required_resource varchar(50),
    eta_minutes integer DEFAULT 10,
    status varchar(20) DEFAULT 'EN_ROUTE',
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    vitals jsonb
);

CREATE TABLE IF NOT EXISTS public.ref_logs (
    id serial PRIMARY KEY,
    request_id varchar(50) NOT NULL,
    patient_id varchar(50),
    severity varchar(20),
    required_resource varchar(50),
    ambulance_lat double precision,
    ambulance_lon double precision,
    recommended_hospital varchar(50),
    alternatives text[],
    confidence_score double precision,
    ai_reasoning text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    vitals jsonb
);

CREATE TABLE IF NOT EXISTS public.users (
    user_id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL,
    facility_id text,
    created_at timestamp without time zone DEFAULT now()
);
