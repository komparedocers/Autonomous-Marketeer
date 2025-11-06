-- PostgreSQL initialization script
-- This script creates the database schema and seed data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables will be created by SQLAlchemy/Alembic migrations
-- This script is for additional setup

-- Create default admin user (password: demo123)
-- Password hash for 'demo123' using bcrypt
INSERT INTO tenants (name, plan, status, created_at, updated_at)
VALUES ('Demo Company', 'free', 'active', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- The API service will handle user creation on first run
-- See services/api/app/core/config.py for DEFAULT_TENANT_* variables
