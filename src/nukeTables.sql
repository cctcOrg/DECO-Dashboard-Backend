-- SQL script that automates DESTROYING of tables.
\connect newdb

DROP SCHEMA public CASCADE;
CREATE SCHEMA public; 
GRANT ALL ON SCHEMA public TO postgres; 
GRANT ALL ON SCHEMA public TO public;
