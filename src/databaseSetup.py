import sys
import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

CollectionTypeEnum = ENUM(
   'Computer',
   'Storage Device',
   'Mobile Device',
   'Targeted',
   'Network Storage',
   'Remote Location',
   'Cloud/Email',
   name='CollectionTypeEnum')

MediaStatusEnum = ENUM(
   'Removed from system',
   'Physical device only (not connected to a system)',
   'Not visible (network/remote)',
   'Remained in system or enclosure during acquisition',
   'Live system acquisition',
   'Encrypted',
   name='MediaStatusEnum')


ShutDownMethodEnum = ENUM(
   'Unknown',
   'Hard',
   'Soft',
   'Left Running',
   name='ShutDownMethodEnum')

def dump_datetime( value ):
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class FileUpload( Base ):
    __tablename__ = 'file_upload'
    id = Column(Integer, primary_key = True)
    fileName = Column( String(), nullable = False)
    pathToFile = Column( String(), nullable = False)
    dateOfUpload = Column( DateTime, nullable = False )

class Users( Base ):
    __tablename__ = 'users'
    id = Column (Integer, primary_key = True)
    email = Column( String(), unique=True, nullable = False)
    lastName = Column( String(), nullable = False)
    firstName = Column( String(), nullable = False)    
    case_summary = relationship('CaseSummary', backref="users") 
    deviceDescription = relationship('DeviceDescription', uselist=False, backref="users")
    digitalMediaDesc = relationship('DigitalMediaDesc', uselist=False, backref="users")
    imagingInformation = relationship('ImagingInformation', uselist=False, backref="users")
    relevantFiles = relationship('RelevantFiles', uselist=False, backref="users")

    @propery
    def serialize( self ):
        return {
                  'id'          : self.id,
                  'email'       : self.email,
                  'lastName'    : self.lastName,
                  'firstName'   : self.firstName
               }

   
class CaseSummary( Base ):
    __tablename__ = 'case_summary'
    id = Column( Integer, primary_key = True)
    dateReceived = Column( DateTime, nullable = False )
    caseNumber = Column( Integer, nullable = False )
    caseDescription = Column( String(), nullable = False)
    deviceDesc = Column( String(), nullable = False)
    suspectName = Column( String(), nullable = False)
    collectionLocation = Column( String(), nullable = False)
    examinerNames = Column( String(), nullable = False)
    labId = Column( Integer, unique = True, nullable = False)
    userId = Column( Integer, ForeignKey('users.id'), unique=False, nullable=False)

    deviceDescription = relationship('DeviceDescription', uselist=False, backref="case_summary")

    @property
    def serialize( self ):
        return {
                'id'                : self.id,
                'dateReceived'      : dump_datetime(self.dateReceived),
                'caseNumber'        : self.caseNumber,
                'deviceDesc'        : self.deviceDesc,
                'suspectName'       : self.suspectName, 
                'collectionLocation': self.collectionLocation,
                'labId'             : self.labId
                }
class DeviceDescription( Base ):
    __tablename__ = 'device_description'
    id = Column( Integer, primary_key = True)
    deviceDescription = Column( String(), nullable = False)
    make = Column( String(), nullable = False)
    model = Column( String(), nullable = False)
    serialNumber = Column( Integer, nullable = False)
    deviceStatus = Column( String(), nullable = False)
    shutDownMethod = Column( ShutDownMethodEnum, nullable = False)
    systemDateTime = Column( DateTime, nullable = False)
    localDateTime = Column( DateTime, nullable = False)
    typeOfCollection = Column( CollectionTypeEnum, nullable = False)
    mediaStatus = Column( MediaStatusEnum, nullable = False)
    userId = Column( Integer, ForeignKey('users.id'), unique=False, nullable=False)
    caseSummaryId = Column( Integer, ForeignKey('case_summary.id'), unique=False, nullable=False)
    digitalMediaDesc = relationship('DigitalMediaDesc', uselist=False, backref="device_description")
    @property
    def serialize( self ):
        return{
                'id'                : self.id,
                'deviceDesc'        : self.deviceDescription,
                'make'              : self.make,
                'model'             : self.model, 
                'serialNumber'      : self.serialNumber,
                'deviceStatus'      : self.deviceStatus,
                'shutDownMethod'    : self.shutDownMethod,
                'systemDateTime'    : dump_datetime(self.systemDateTime),
                'localDateTime'     : dump_datetime(self.localDateTime),
                'typeOfCollection'  : self.typeOfCollection,
                'mediaStatus'       : self.mediaStatus
              }

class DigitalMediaDesc( Base):
    __tablename__ = "digital_media_desc"
    id = Column( Integer, primary_key = True)
    storageId = Column( Integer, nullable = False)
    make = Column( String(), nullable = False)
    model = Column( String(), nullable = False)
    serialNumber = Column( Integer, nullable = False)
    capacity = Column( Integer, nullable = False)
    userId = Column( Integer, ForeignKey('users.id'), unique=False, nullable=False)
    deviceDescId = Column( Integer, ForeignKey('device_description.id'), unique=False, nullable=False)
    imagingInformation = relationship('ImagingInformation', uselist=False, backref="digital_media_desc")
    @property
    def serialize( self ):
        return {
                 'id'              : self.id,
                 'storageId'       : self.storageId,
                 'make'            : self.make,
                 'model'           : self.model,
                 'serialNumber'    : self.serialNumber,
                 'capacity'        : self.capacity
               }

   
class ImagingInformation( Base ):
    __tablename__ = "imaging_information"
    id = Column( Integer, primary_key = True)
    writeBlockMethod = Column( String(), nullable = False)
    imagingTools = Column( String(), nullable =False)
    format = Column( String(), nullable=False)
    primaryStorageMediaId = Column( Integer, nullable = False)
    primaryStorageMediaName = Column( String(), nullable =False)
    backupStorageMediaId =Column( Integer, nullable = False)
    backupStorageMediaName = Column( String(), nullable =False)
    postCollection = Column( String(), nullable =False)
    size = Column( Integer, nullable = False)
    notes = Column( String(), nullable =False)
    userId = Column( Integer, ForeignKey('users.id'), unique=False, nullable=False)
    digitalMediaDescId = Column( Integer, ForeignKey('digital_media_desc.id'), unique=False, nullable=False)
    relevantFiles = relationship('RelevantFiles', uselist=False, backref="imaging_information")
    @property
    def serialize( self ):
        return{
                'id'                       : self.id,
                'writeBlockMethod'         : self.writeBlockMethod,
                'imagingTools'             : self.imagingTools,
                'format'                   : self.format,
                'primaryStorageMediaId'    : self.primaryStorageMediaId,
                'primaryStorageMeidaName'  : self.primaryStorageMediaName,
                'backupStorageMediaId'     : self.backupStorageMediaId,
                'backupStorageMediaName'   : self.backupStorageMediaName,
                'postCollection'           : self.postCollection,
                'size'                     : self.size,
                'notes'                    : self.notes
              }

class RelevantFiles( Base):
    __tablename__ = "relevant_files"
    id = Column( Integer, primary_key = True)
    fileName = Column( String(), nullable =False)
    path = Column( String(), nullable =False)
    contentDesc = Column( String(), nullable =False)
    size = Column( Integer, nullable = False)
    suggestedReviewPlatform = Column( String(), nullable =False)
    notes = Column( String(), nullable =False)
    userId = Column( Integer, ForeignKey('users.id'), unique=False, nullable=False)
    imagingInfoId = Column( Integer, ForeignKey('imaging_information.id'), unique=False, nullable=False)

    @property
    def serialize( self ):
        return{
                'id'                      : self.id,
                'fileName'                : self.fileName,
                'path'                    : self.path,
                'contentDesc'             : self.contentDesc,
                'size'                    : self.size,
                'suggestedReviewPlatform' : self.suggestedReviewPlatform,
                'notes'                   : self.notes
              }

engine = create_engine( 'postgresql://postgres@localhost/dbnew')
Base.metadata.create_all( engine)
