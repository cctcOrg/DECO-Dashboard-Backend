/* File containing create table statements for Digital Evidence Collection Worksheet 
 * database. Used so that everyone has the same database structure on their 
 * local machine.
 */
CREATE USER cctc WITH SUPERUSER ENCRYPTED PASSWORD 'CCTC@CampSLO';

DROP DATABASE IF EXISTS dashboarddb;
CREATE DATABASE bashboarddb;

DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS CaseSummary;

DROP TABLE IF EXISTS Overview;
DROP TABLE IF EXISTS EvidenceSummary;
DROP TABLE IF EXISTS CollectionStatus;
DROP TABLE IF EXISTS MediaStatus;
DROP TABLE IF EXISTS DeviceDetails;
DROP TABLE IF EXISTS DigitalMediaDesc;
DROP TABLE IF EXISTS ImagingInfo;
DROP TABLE IF EXISTS NetworkCollectionInfo;
DROP TABLE IF EXISTS CloudCollectionInfo;
DROP TABLE IF EXISTS NetworkCollectionInfo;
DROP TABLE IF EXISTS Notes;


CREATE TABLE Overview (
   worksheetId SERIAL PRIMARY KEY,
   deviceDesc TEXT NOT NULL,
   imageName TEXT NOT NULL,
   primaryStorageMediaID INT UNIQUE NOT NULL,
   backupStorageMediaID INT UNIQUE NOT NULL
);

-- Create enum type for type of collection.
CREATE TYPE CollectionType AS ENUM (
   'Computer', 
   'Storage Device', 
   'Mobile Device', 
   'Targeted', 
   'Network Storage', 
   'Remote Location',
   'Cloud/Email'
);

CREATE TABLE EvidenceSummary (
   id SERIAL PRIMARY KEY,
   dateOfCollection TIMESTAMP NOT NULL,
   caseNumber INT NOT NULL,
   subjectName TEXT NOT NULL,
   examinerName TEXT NOT NULL,
   collectionLocation TEXT NOT NULL,
   typeOfCollection CollectionType NOT NULL,
   worksheetId INT REFERENCES Overview(worksheetId)
);

-- Create enum type for the various media statuses.
CREATE TYPE MediaStatus AS ENUM (
   'Removed from system', 
   'Physical device only (not connected to a system)', 
   'Not visible (network/remote)', 
   'Remained in system or enclosure during acquistion', 
   'Live system acquisition', 
   'Encrypted');

/* This table exists to support ability for user to assoicate multiple
   media statues with one type of collection. Need primary key to be 
   collectionStatusId AND mediaStatus for one to many relationship. */
CREATE TABLE MediaStatus (
   evidenceSummaryId REFERENCES EvidenceSummary(id)
   mediaStatus MediaStatus NOT NULL,
   PRIMARY KEY(collectionStatusId, mediaStatus)
);

-- Create enum type for the various shut down methods.
CREATE TYPE ShutDownMethod AS ENUM (
   'Unknown',
   'Hard',
   'Soft',
   'Left Running'
);

CREATE TABLE DeviceDetails (
   id SERIAL PRIMARY KEY,
   make TEXT NOT NULL,
   model TEXT NOT NULL,
   serialNumber INT NOT NULL,
   deviceStatus TEXT NOT NULL,
   shutdownMethod ShutDownMethod NOT NULL,
   systemDateTime TIMESTAMP NOT NULL,
   localDateTime TIMESTAMPTZ NOT NULL,
   worksheetId INT REFERENCES Overview(worksheetId)
);

CREATE TABLE DigitalMediaDesc (
   id SERIAL PRIMARY KEY,
   make TEXT NOT NULL,
   model TEXT NOT NULL,
   oemStorageCapacity INT NOT NULL,
   serialNumber INT NOT NULL,
   internalSerialNumber TEXT NOT NULL,
   interface TEXT NOT NULL,
   mediaType TEXT NOT NULL,
   worksheetId INT REFERENCES Overview(worksheetId)
);

-- Backend will standardize write block methods if not of type 'other'.
CREATE TABLE ImagingInfo (
   id SERIAL PRIMARY KEY,
   writeBlockMethod TEXT NOT NULL,
   imagingTools TEXT NOT NULL,
   format TEXT NOT NULL,
   worksheetId INT REFERENCES Overview(worksheetId)
);

CREATE TABLE NetworkCollectionInfo (
   id SERIAL PRIMARY KEY,
   connection TEXT NOT NULL,
   collectionType TEXT NOT NULL,
   path TEXT NOT NULL,
   worksheetId INT REFERENCES Overview(worksheetId)
);

CREATE TABLE CloudCollectionInfo (
   id SERIAL PRIMARY KEY,
   toolUsed TEXT NOT NULL,
   userAccountInfo TEXT NOT NULL,
   worksheetId INT REFERENCES Overview(worksheetId)
);

CREATE TABLE Notes (
   id SERIAL PRIMARY KEY,
   postCollection TEXT NOT NULL,
   generalNotes TEXT,
   worksheetId INT REFERENCES Overview(worksheetId)
);
