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

class FileUpload( Base ):
    __tablename__ = 'file_upload'
    id = Column(Integer, primary_key = True)
    fileName = Column( String(), nullable = False)
    pathToFile = Column( String(), nullable = False)
    dateOfUpload = Column( DateTime, nullable = False )

class User( Base ):
    __tablename__ = 'user'
    id = Column (Integer, primary_key = True)
    email = Column( String(), unique=True, nullable = False)
    lastName = Column( String(), nullable = False)
    firstName = Column( String(), nullable = False)    
    overview = relationship('Overview', backref="user") 

# This table maps relationship between a user and the worksheets they've made
# One to many

def dump_datetime( value ):
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Overview( Base ):
    __tablename__ = 'overview'
    id = Column( Integer, primary_key = True)
    dateOfSubmittal = Column( DateTime, nullable = False )
    deviceDesc = Column( String(), nullable = False)
    imageName = Column( String(), nullable = False)
    primaryStorageMediaId = Column( String(), nullable = False)
    backupStorageMediaId = Column( String(), nullable = False)
    userId = Column( Integer, ForeignKey('user.id'), unique=False, nullable=False)

    evidenceSummary = relationship('EvidenceSummary', uselist=False, backref="overview")
    mediaStatus = relationship('MediaStatus', uselist=False, backref="overview")
    deviceDetails = relationship('DeviceDetails', uselist=False, backref="overview")
    digitalMediaDesc = relationship('DigitalMediaDesc', uselist=False, backref="overview")
    imagingInformation = relationship('ImagingInformation', uselist=False, backref="overview")
    networkCollectionInfo = relationship('NetworkCollectionInfo', uselist=False, backref="overview")
    cloudCollectionInfo = relationship('CloudCollectionInfo', uselist=False, backref="overview")
    notes = relationship('Notes', uselist=False, backref="overview")
    @property
    def serialize( self ):
        return {
                'id'              : self.id,
                'dateOfSubmittal' : dump_datetime(self.dateOfSubmittal),
                'deviceDesc'      : self.deviceDesc,
                'imageName'       : self.imageName,
                'primaryStorageMediaId' : self.primaryStorageMediaId,
                'backupStorageMediaId'  : self.backupStorageMediaId
                }


class EvidenceSummary( Base ):
    __tablename__ = 'evidence_summary'
    id = Column( Integer, primary_key = True)
    # not sure how DateTime works
    dateOfCollection = Column( DateTime, nullable = False)
    caseNumber = Column( Integer, nullable = False)
    subjectName = Column( String(), nullable = False)
    examinerName = Column( String(), nullable = False)
    collectionLocation = Column( String(), nullable = False)
    typeOfCollection = Column(CollectionTypeEnum, nullable = False)
    worksheetId = Column( Integer, ForeignKey('overview.id'))
    mediaStatus = relationship("MediaStatus", uselist=False, backref='evidence_summary')
    @property
    def serialize( self ):
        return {
                'dateOfCollection'  : dump_datetime( self.dateOfCollection ),
                'caseNumber'        : self.caseNumber,
                'subjectName'       : self.subjectName,
                'examinerName'      : self.examinerName,
                'collectionLocation': self.collectionLocation,
                'typeOfCollection'  : self.typeOfCollection,
                'worksheetId'       : self.worksheetId
                }


class MediaStatus( Base ):
    __tablename__ = 'media_status'
    evidenceSummaryId = Column( Integer, ForeignKey('evidence_summary.id'), primary_key = True)
    mediaStatus = Column( MediaStatusEnum, primary_key = True)
    worksheetId = Column( Integer, ForeignKey('overview.id'))
    
class DeviceDetails( Base ):
    __tablename__ = 'device_details'
    id = Column( Integer, primary_key = True)
    make = Column( String(), nullable = False)
    model = Column( String(), nullable = False)
    serialNumber = Column( Integer, nullable = False)
    deviceStatus = Column( String(), nullable = False)
    shutDownMethod = Column( ShutDownMethodEnum, nullable = False)
    systemDateTime = Column( DateTime, nullable = False)
    # not sure how DateTime works
    localDateTime = Column( DateTime, nullable = False)
    worksheetId = Column( Integer, ForeignKey('overview.id'))

class DigitalMediaDesc( Base ):
    __tablename__ = 'digital_mediaDesc'
    id = Column( Integer, primary_key = True)
    dmdMake = Column( String(), nullable = False)
    dmdModel = Column( String(), nullable = False)
    oemStorageCapacity = Column( Integer, nullable = False)
    dmdSerialNumber = Column( Integer, nullable = False)
    internalSerialNumber = Column( String(), nullable = False)
    interface = Column( String(), nullable = False)
    mediaType = Column( String(), nullable = False)
    worksheetId = Column( Integer, ForeignKey('overview.id'))

class ImagingInformation( Base ):
    __tablename__ = "imaging_information"
    id = Column( Integer, primary_key = True)
    writeBlockMethod = Column( String(), nullable = False)
    imagingTools = Column( String(), nullable =False)
    format = Column( String(), nullable=False)
    worksheetId = Column( Integer, ForeignKey( 'overview.id'))

class NetworkCollectionInfo( Base ):
    __tablename__ = 'network_collectionInfo'
    id = Column( Integer, primary_key = True)
    connection = Column( String(), nullable=False )
    collectionType = Column( String(), nullable=False)
    path = Column( String(), nullable = False)
    worksheetId = Column( Integer, ForeignKey( 'overview.id'))

class CloudCollectionInfo( Base):
    __tablename__ = 'cloud_collection_info'
    id = Column( Integer, primary_key = True)
    toolUsed = Column( String(), nullable=False)
    userAccountInfo = Column( String(), nullable=False)
    worksheetId = Column( Integer, ForeignKey( 'overview.id'))

class Notes( Base ):
    __tablename__ = 'notes'
    id = Column( Integer, primary_key = True) 
    postCollection = Column( String(), nullable=False )
    generalNotes = Column( String())
    worksheetId = Column( Integer, ForeignKey( 'overview.id'))


engine = create_engine( 'postgresql://postgres@localhost/dbnew')
Base.metadata.create_all( engine)
