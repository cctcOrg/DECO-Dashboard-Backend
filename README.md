# CCTC Digital Evidence Collection Dashboard Backend

This is documentation for the CCTC Digital Evidence Collection (DECO) 
Dashboard, explaining the backend development aspect ranging from setting up 
the development environment to developing the backend server for dashboard. 
This is California’s first collaborative forensic data display that will allow 
investigators to track cases digitally.

| Contributors  | Time Period        |
|           --- | ---                |
| Duc Dao       | Summer, Fall 2017  |
| Jackson Kurtz | Summer 2017        |
| Tyler Nash    | Summer 2017        |

# 1.0 Running the Backend

There are two ways to run the backend. We used section 1.1 for development on our local and local Fedora server (codenamed PizzaGoldFish) and section 1.2 for deployment on Amazon Web Services (AWS).

## 1.1 Running server WITHOUT Docker and Nginx (Files are in src directory)
1. Install PostgreSQL and Python files in `requirements.txt`
2. Create Postgres database (must use root user or configure user to have superuser privileges)
    1. Start Postgres application
    2. Type `psql` in terminal to enter psql shell
    3. To create database, type `CREATE database {db name};`
    4. Exit with `\q`
3. Edit `databaseSetup.py` and `flaskServer.py` as described in Setup section below
4. Create tables with `python databaseSetup.py`
5. Run server with `python flaskServer.py`

## 1.2 Running server WITH Docker and Nginx (Files in DockerTest directory)
1. Install PostgreSQL
2. Create database with directions listed above
3. Edit `databaseSetup.py` and `main.py` instead of `flaskServer.py` as described in Setup section below
4. Create tables with `python databaseSetup.py`
5. Follow this guide to setup and run the docker container: https://ianlondon.github.io/blog/deploy-flask-docker-nginx/

# 2.0 Setup

Text in < > are fields descriptions, remove them when using actual value. Edit the following lines with respect to hosting machine:

**databaseSetup.py**
( line 230 ) `engine = create_engine( uri to database )`

Example URI: 'postgresql://postgres@localhost/newdb'

**flaskServer.py**
( line 15 ) `app.config[‘SQLALCHEMY_DATABASE_URI’] = <uri to database>`
( line 22 ) `app.config[‘UPLOAD_FOLDER’] = <file path to upload directory>`
( line 425 ) `app.run(host = app.run(host = <ip of host>, port = <port number> ), debug=True)`

# 3.0 Backend Overview
The main components of the backend are:
* Flask, a Python web microframework as our server
* SQLAlchemy, Python SQL toolkit and object-relational mapper
* PostgreSQL database
The server uses Flask which we chose due to its simplicity and ease of use. Flask is highly compatible with the Python toolkit and object-relational mapper SQLAlchemy, which we used to communicate with the PostgreSQL database.

This stack is functional on a local machine for testing purposes but will crash if too many requests are sent in a short period of time. It also will not support https, only http. When hosting the server and database on AWS, we used a Docker container with Nginx to fix the aforementioned problems and allow for increased scalability. However, to properly scale to a larger application on AWS, deploying the application using Amazon’s Elastic Beanstalk is probably necessary.

## 3.1 PostgreSQL
PostgreSQL was chosen for its scalability and variety of features. Creating databases, user management, and other basic commands are done through the Postgres shell which is simply run by typing “psql” in the terminal.
A description of some of the commands we often used to manage the database are in the README.md on the GitHub for this project. To view entries in the database, we used:
* pgAdmin (Windows/Linux)
* PSequel (Mac)
* Postgres shell (terminal)
PSequel is much easier to use in comparison to pgAdmin but is only available on Mac. We mainly used these clients to view entries in the data table but they can also be used to directly edit rows in the database and even delete tables.

## 3.2 databaseSetup.py
There are two Python files that are used to setup and run the backend. The first is databaseSetup.py which is used to create the tables in the Postgres database through SQLAlchemy. It is in this file where column names and types are specified, as well as the relationships between the tables. Below is a list of the column fields and types, as well as a description of the relationship between the tables. This file should be run on a database that was already created in the Postgres shell, but has no tables.

The URI address for the database is specified at the bottom of this file. It requires:
* Username
* Password
* IP address for the database
* Database name at the end
This file also has a second function: it is imported by flaskServer.py so that the server can create entries for each table, which are subsequently inserted into the database.

## 3.3 flaskServer.py
flaskServer.py is run continuously once the database has been properly set up, and acts as a RESTful API that accepts and handles requests from the frontend Angular server. The server uses an extension for Flask called Flask-RESTful that allows the server to function as an API.

The server is able to handle four types of RESTful requests for each table in the database:
* GET
* POST
* PUT
* DELETE

A full description of the endpoints is included later in this documentation.

## 3.4 Docker and Nginx
As described in the backend summary, using a Docker container with an Nginx server allows for a more secure and stable backend API. Additionally, using Docker makes the application more portable as it allows for easy installation of dependencies and setup of a compatible virtual environment. More info can be found in the guide we followed to set up the container: https://ianlondon.github.io/blog/deploy-flask-docker-nginx/.

## 3.5 Amazon Web Servies
To host the backend on AWS, we used Amazon’s Relational Database Service (RDS) for the Postgres database, and Amazon’s Elastic Compute Cloud (EC2) for the Flask/Docker/Nginx server. Setting each of these instances up is mostly straightforward but here are a few tips that might save some time:
* Command to ssh into the Ec2 instance: ssh -i {pem file} {username@ipaddress}
* The .pem file used to authenticate and ssh into the EC2 instance must have its access permissions changed using the following command to work properly: chmod 700 {filename}.pem
* To allow inbound connections, the EC2 instance must have properly configured inbound rules and security group, which are listed in the last column of the EC2 instance information. We set the rule to allow inbound http connections on port 80 from anywhere when testing.
One of our eventual goals was to also use Amazon’s Cognito service to set up a better system of user authentication that could potentially be handled in the front end. This not only would be much easier and more secure than if we set it up ourselves, but it also could be paired with Cognito’s Federated Identities to include security group and cross platform features.

# 4.0 PostgreSQL "Cheat Sheet"

### In psql shell: ###
   * Running SQL statements in a file:     `\i [fileName]`
   * List all databases:                   `\list` or `\l`
   * List all tables for current database: `\dt`
   * Connect to a different database:      `\connect [dbName]`
   * Create database: 	                   `\create database [dbName]`
   * Drop all tables:       		   `DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;`

### From terminal/command line: ###
   * Running SQL statements in a file:     `psql -f [fileName]`
   
   * If you run `psql` and get `psql: could not connect to server: No such 
     file or directory`:
        1. As a normal terminal user, edit the postgresql.conf. Path is
           `/etc/postgres/9.3/main/postgresql.conf`. Need to open as sudo.
        2. Enable or add `listen_addresses = '*'`
        3. Restart database engine: `sudo service postgresql restart`

# 5.0 CURL Request to Flask Server
Post request that creates 'User' entry:
`curl -H "Content-Type: application/json" -X POST -d 
'{"email": "someEmail@domain.com", 
"lastName": "Jones", 
"firstName": "Alex"}' 
http://localhost:5000/evd/user`

# 6.0 Resources 
**AWS Docker Nginx Tutorial**
https://ianlondon.github.io/blog/deploy-flask-docker-nginx/

**Flask User Session Management**
https://flask-login.readthedocs.io/en/latest/

**Warrant Serverless Authentication - Python library for using AWS Cognito**
https://github.com/capless/warrant
