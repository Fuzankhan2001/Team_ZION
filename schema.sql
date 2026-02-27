-- ===============================
-- AIRA-Med Database Schema
-- Phase 1: Core tables only
-- ===============================

CREATE TABLE IF NOT EXISTS public.hospitals (
    facility_id text PRIMARY KEY,
    name text NOT NULL,
    city text NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.users (
    user_id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL,
    facility_id text,
    created_at timestamp without time zone DEFAULT now()
);
