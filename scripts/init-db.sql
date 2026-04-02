-- Initialize database for expense-tracker
-- Database is already created via POSTGRES_DB env var, just set permissions
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'expense_tracker') THEN
        CREATE DATABASE expense_tracker ENCODING 'UTF8' LOCALE 'en_US.UTF-8';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
ALTER DATABASE expense_tracker OWNER TO expense_user;
