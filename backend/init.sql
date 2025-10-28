-- Initial database setup for Levitiis production

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'levitiis_user') THEN
        CREATE ROLE levitiis_user WITH LOGIN PASSWORD 'secure_password_123';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE levitiis_prod TO levitiis_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO levitiis_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO levitiis_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO levitiis_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO levitiis_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO levitiis_user;

-- Create indexes for better performance (will be created by Alembic migrations)
-- These are just examples of what might be needed

-- Performance tuning settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();