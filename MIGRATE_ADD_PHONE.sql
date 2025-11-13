-- Migration: Add missing columns to voters table for OTP support
-- Run this script in your MySQL client to update the existing voters table

USE smart_voting_system;

-- Check if columns exist before adding (helps avoid errors if running multiple times)
ALTER TABLE voters
ADD COLUMN pno VARCHAR(20) DEFAULT NULL IF NOT EXISTS,
ADD COLUMN state VARCHAR(100) DEFAULT NULL IF NOT EXISTS,
ADD COLUMN d_name VARCHAR(100) DEFAULT NULL IF NOT EXISTS;

-- Verify the columns were added
DESC voters;
