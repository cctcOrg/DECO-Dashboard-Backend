# CCTC Evidence Backend

GitHub page for CCTC Evidence Backend Team (Duc, Jackson, and Tyler).

# PostgreSQL "Cheat Sheet"

In psql shell:
   * Running SQL statements in a file:     `\i [fileName]`
   * List all databases:                   `\list` or `\l`
   * List all tables for current database: `\dt`
   * Connect to a different database:      `\connect [dbName]`
   * Create database: 	                   `\create database [dbName]`
   * Drop all tables:       		   `DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;`

From terminal/command line:
   * Running SQL statements in a file:     `psql -f [fileName]`
   
   * If you run `psql` and get `psql: could not connect to server: No such 
     file or directory`:
        1. As a normal terminal user, edit the postgresql.conf. Path is
           `/etc/postgres/9.3/main/postgresql.conf`. Need to open as sudo.
        2. Enable or add `listen_addresses = '*'`
        3. Restart database engine: `sudo service postgresql restart`

# CURL Request to Flask Server

Post request that creates 'Overview' object:
`curl -H "Content-Type: application/json" -X POST -d '{"deviceDesc": "description", "imageName": "iname", "primaryStorageMediaId": 123, "backupStorageMediaId": 456}' http://localhost:5000/form`
