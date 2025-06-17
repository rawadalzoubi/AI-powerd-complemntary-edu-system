-- Add password_reset_token column
ALTER TABLE eduAPI_user ADD COLUMN password_reset_token VARCHAR(64) NULL;

-- Add password_reset_expires column
ALTER TABLE eduAPI_user ADD COLUMN password_reset_expires DATETIME NULL; 