-- AI Nurse Florence - Database Initialization Script
-- This script sets up the production database with proper security

-- Create the main database (handled by POSTGRES_DB env var)
-- CREATE DATABASE florence_db;

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS public;

-- Grant permissions to the florence user
GRANT ALL PRIVILEGES ON DATABASE florence_db TO florence;
GRANT ALL PRIVILEGES ON SCHEMA public TO florence;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set up initial tables (these will be created by Alembic migrations)
-- But we can create some basic structure if needed

-- Example: User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Example: Audit log table for medical data access
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint VARCHAR(255) NOT NULL,
    query_data JSONB,
    response_status INTEGER,
    user_ip INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    request_id VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_endpoint ON audit_log(endpoint);

-- Set up row-level security policies if needed
-- ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Cleanup old sessions function
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to cleanup expired sessions (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-sessions', '0 * * * *', 'SELECT cleanup_expired_sessions();');

COMMIT;
