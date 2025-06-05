-- Migration script to add new columns to existing tables
-- Run this SQL in your Supabase SQL editor if you have an existing database

-- Add reason column to followup_questions table
ALTER TABLE followup_questions
ADD COLUMN IF NOT EXISTS reason TEXT;

-- Add model and temperature columns to prompts table
ALTER TABLE prompts
ADD COLUMN IF NOT EXISTS model VARCHAR(100) DEFAULT 'gemini-2.0-flash';

ALTER TABLE prompts
ADD COLUMN IF NOT EXISTS temperature DECIMAL(3,2) DEFAULT 0.7;

-- Optional: Add comments to document the changes
COMMENT ON COLUMN followup_questions.reason IS 'Explanation of why the follow-up question is needed';
COMMENT ON COLUMN prompts.model IS 'AI model to use for this prompt (e.g., gemini-2.0-flash, gemini-1.5-flash)';
COMMENT ON COLUMN prompts.temperature IS 'Temperature setting for AI generation (0.0 to 1.0)';
