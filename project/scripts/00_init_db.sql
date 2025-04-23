CREATE DATABASE the_filter_factory;

\c the_filter_factory

-- Create table for denylist
CREATE TABLE IF NOT EXISTS denylist (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for allowlist
CREATE TABLE IF NOT EXISTS allowlist (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
