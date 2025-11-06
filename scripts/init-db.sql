-- PostgreSQL initialization script
-- Tables are created by SQLAlchemy in the API service
-- This script is for any additional database setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: The API service will create tables and seed data on first run
-- See services/api/app/main.py startup event
