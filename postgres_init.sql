-- run this script with postgres superuser
-- sudo -u postgres psql -f ./postgres_init.sql

-- Create user elearn_app with password
CREATE USER elearn_app WITH PASSWORD 'elearn_app';

-- Grant database creation privilege needed for unit test database setup
ALTER USER elearn_app CREATEDB;

-- Create the main app database owned by elearn_app
CREATE DATABASE elearn_db OWNER elearn_app;

-- Grant all privileges on the app database
GRANT ALL PRIVILEGES ON DATABASE elearn_db TO elearn_app;

-- Set default settings for elearn_app
ALTER ROLE elearn_app SET client_encoding TO 'utf8';
ALTER ROLE elearn_app SET default_transaction_isolation TO 'read committed';
ALTER ROLE elearn_app SET timezone TO 'UTC';
