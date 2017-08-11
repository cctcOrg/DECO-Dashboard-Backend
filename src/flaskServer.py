from flask import Flask, send_file
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Response, jsonify, request, redirect, render_template, url_for
from sqlalchemy import create_engine
from databaseSetup import Users, CaseSummary, DeviceDesc, DigitalMediaDesc, ImageInfo, RelevantFiles  
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import datetime
from pathlib import Path

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/newdb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cctc_user:cctc@localhost/dashboarddb'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cctc:CampSLOcctc@dashdb.cftpr0gv1icv.us-west-2.rds.amazonaws.com:5432/dashdb'
app.debug=True
api = Api(app)
db = SQLAlchemy(app)
CORS(app)
UPLOAD_FOLDER = '/Users/jacksonkurtz/Documents/Code/CCTC/DashboardBackend/Uploads'     
#UPLOAD_FOLDER = '/srv/http/DigitalEvidenceCollection/Backend/Uploads'
#UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# updates object fields based on the JSON dictionary sent
# used in PUT requests
def iterateJsonUpdate( row, data, ignore=None ):
    if ignore:
        for key in ignore:
            try:
                del data[key]
            except:
                pass
    for key in data.keys():
        setattr(row, key, data[key])
    return row

class UserInfo(Resource):
    def get(self):
        # Query User table by email 
        user = db.session.query(Users).filter_by(email = request.args.get('email')).first()
        return user.serialize

    # Create a new user 
    def post(self):
        post = "[POST USER] "
        
        print(post + "Getting data from JSON...")
        data = request.get_json()
        print( "data: ", data )
        print(post + "Creating row for DB insertion...")
        users = Users( 
            email = data['email'],
            passwordHash = data['passwordHash'],
            lastName = data['lastName'],
            firstName = data['firstName'] )

        print(post + "Inserting into DB...")
        # Stage and commit to database
        db.session.add(users)
        db.session.commit()

        print(post + "RETURNING 200")
        return 200

    def put( self ):
        put = "[PUT USER] "
        print(put + "Getting data from JSON...")
        data = request.get_json()
        print( put + "Editing row of user table...")
        user = db.session.query(Users).filter_by( email = request.args.get('email')).first() 
        iterateJsonUpdate( user, data, ['email']) 
        print( put + "Inserting into DB...")
        db.session.commit()
        return 200

    def delete( self ):
        db.session.query( Users ).filter_by( email = request.args.get('email')).delete()
        db.session.commit()
        return 200

class Case(Resource):
   # Return case summary
    def get(self, userId):
        # Get a specific case for logged in user
        if request.args.get('caseId'):
            case = db.session.query(CaseSummary).filter_by(id = request.args.get('caseId'), userId = userId).one()
            return case.serialize
        # Get all cases for logged in user
        else:
            cases = db.session.query(CaseSummary).filter_by(userId = userId).all()
            return { "case_summary_list": [case.serialize for case in cases] }
   
    # Create a new case
    def post( self, userId ):
        post = "[POST CASE] "
        
        print(post + "Getting data from JSON...")
        # Get JSON data from frontend
        data = request.get_json()

        print(post + "Creating row for DB insertion...")
        # Create new case object, populated with values from JSON data
        user = db.session.query(Users).filter_by(id = userId).one()
        case = CaseSummary(
            dateReceived = data['dateReceived'],
            caseNumber = data['caseNumber'],
            caseDescription = data['caseDescription'],
            suspectLastName = data['suspectLastName'],
            suspectFirstName = data['suspectFirstName'],
            examinerLastName = data['examinerLastName'],
            examinerFirstName = data['examinerFirstName'],
            collectionLocation = data['collectionLocation'],
            labId = data['labId'],
            users = user )

        print(post + "Inserting into DB...")
        # Stage case for commit to database
        db.session.add(case)
        # Commit case to database
        db.session.commit()
        return 200

    def put( self, userId ):
        put = "[PUT CASE] "
        print(put + "Getting data from JSON...")
        data = request.get_json()
        print( put + "Editing row of case table...")
        case = db.session.query(CaseSummary).filter_by( id = request.args.get('caseId')).first() 
        iterateJsonUpdate( case, data ) 
        print( put + "Committing to DB...")
        db.session.commit()
        return 200
   
    def delete( self, userId ):
        db.session.query(CaseSummary).filter_by(id = request.args.get('caseId')).delete()
        db.session.commit()
        return 200

class Device(Resource):
    def get(self, userId, caseId):
        get = "[GET DEV] "
        
        # Get a specific device for the specified case for logged in user
        if request.args.get('deviceId'):
            device = db.session.query(DeviceDesc).filter_by(id = request.args.get('deviceId'), userId = userId).one()
            return device.serialize
        # Get all devices for specified case for logged in user
        else:
            print(get + "Getting all devices belonging to case, caseId...")
            devices = db.session.query(DeviceDesc).filter_by(caseSummaryId = caseId, userId = userId).all()
        
            print(get + "Returning JSON...")
            return { "device_list": [device.serialize for device in devices] }

    def post(self, userId, caseId):
        post = "[POST DEV]"

        print(post + "Getting JSON...")
        data = request.get_json()

        print(post + "Creating entry for database...")
        users = db.session.query(Users).filter_by(id = userId).one()
        case_summary = db.session.query(CaseSummary).filter_by(id = caseId).one()
        deviceDesc=DeviceDesc( 
                deviceDescription = data['deviceDescription'],
                make = data['make'],
                model = data['model'],
                serialNumber = data['serialNumber'],
                deviceStatus = data['deviceStatus'],
                shutDownMethod = data['shutDownMethod'],
                systemDateTime = data['systemDateTime'],
                localDateTime = data['localDateTime'],
                typeOfCollection = data['typeOfCollection'],
                mediaStatus = data['mediaStatus'],
                users = users,
                case_summary = case_summary )
        
        print(post + "Adding to database...")
        db.session.add( deviceDesc )
        db.session.commit()
        return 200
    
    def put( self, userId, caseId ):
        put = "[PUT DEVICE] "
        print(put + "Getting data from JSON...")
        data = request.get_json()
        print( put + "Editing row of device table...")
        device = db.session.query(DeviceDesc).filter_by( id = request.args.get('deviceId')).first() 
        iterateJsonUpdate( device, data ) 
        print( put + "Committing to DB...")
        db.session.commit()
        return 200

    def delete( self, userId, caseId ):
        db.session.query( DeviceDesc ).filter_by( id = request.args.get("deviceId")).delete()
        db.session.commit()
        return 200

class Media(Resource):
    def get(self, userId, caseId, deviceId):
        # Get specific digital media for specified device/case for logged in user
        if request.args.get('dmId'):
            device = db.session.query(DigitalMediaDesc).filter_by(id = request.args.get('dmId'), userId = userId).one()
            return device.serialize
        # Get all digital media for specified device/case for logged in user
        else:
            medias = db.session.query(DigitalMediaDesc).filter_by(deviceDescId = deviceId, userId = userId).all()
            return { "digital_media_list": [media.serialize for media in medias] }

    def post(self, userId, caseId, deviceId):
        data = request.get_json()

        users = db.session.query(Users).filter_by(id = userId).one()
        deviceDesc = db.session.query(DeviceDesc).filter_by(id = deviceId).one()
        media = DigitalMediaDesc(
                storageId = data['storageId'],
                make = data['make'],
                model = data['model'],
                serialNumber = data['serialNumber'],
                capacity = data['capacity'],
                users = users,
                device_desc = deviceDesc )
       
        db.session.add(media)
        db.session.commit()
        return 200

    def put( self, userId, caseId, deviceId ):
        put = "[PUT MEDIA] "
        print(put + "Getting data from JSON...")
        data = request.get_json()
        print( put + "Editing row of media table...")
        media = db.session.query(DigitalMediaDesc).filter_by( id = request.args.get('dmId')).first() 
        iterateJsonUpdate( media, data ) 
        print( put + "Committing to DB...")
        db.session.commit()
        return 200

    def delete( self, userId, caseId, deviceId  ):
        db.session.query( DigitalMediaDesc ).filter_by( id = request.args.get("dmId")).delete()
        db.session.commit()
        return 200

class Image(Resource):
    def get(self, userId, caseId, deviceId, dmId):
        # Get specific image for specified digital media/device/case for logged in user
        if request.args.get('imgId'):
            image = db.session.query(ImageInfo).filter_by(id = request.args.get('imgId'), userId = userId).one()
            return image.serialize
        # Get all images for specified digital media/device/case for logged in user
        else:
            images = db.session.query(ImageInfo).filter_by(digitalMediaDescId = dmId, userId = userId).all()
            return { "images_list": [image.serialize for image in images ] }

    def post(self, userId, caseId, deviceId, dmId):
        data = request.get_json()
        
        users = db.session.query(Users).filter_by(id = userId).one()
        digital_media_desc = db.session.query(DigitalMediaDesc).filter_by(id = dmId).one()
        imageInfo = ImageInfo( 
                writeBlockMethod = data['writeBlockMethod'], 
                imagingTools = data['imagingTools'],
                format = data['format'],
                primaryStorageMediaId = data['primaryStorageMediaId'],
                primaryStorageMediaName = data['primaryStorageMediaName'],
                backupStorageMediaId = data['backupStorageMediaId'],
                backupStorageMediaName = data['backupStorageMediaName'],
                postCollection = data['postCollection'],
                size = data['size'],
                notes = data['notes'],
                users = users,
                digital_media_desc = digital_media_desc )
        
        db.session.add(imageInfo)
        db.session.commit()
        return 200
    
    def put( self, userId, caseId, deviceId, dmId ):
        put = "[PUT IMAGE] "
        print(put + "Getting data from JSON...")
        data = request.get_json()
        print( put + "Updating row of image table...")
        image = db.session.query(ImageInfo).filter_by( id = request.args.get('imgId')).first() 
        iterateJsonUpdate( image, data ) 
        print( put + "Committing to DB...")
        db.session.commit()
        return 200

    def delete( self, userId, caseId, deviceId, dmId  ):
        db.session.query( ImageInfo ).filter_by( id = request.args.get("imgId")).delete()
        db.session.commit()
        return 200

class File(Resource):   
    # Helper function for File POST
    def sendJSON(self, userId, imgId, request, newPath, fileName, fileSize):
        data = request.form

        print("[POST FILE] Send JSON data related to file just uploaded...")
        users = db.session.query(Users).filter_by(id = userId).one()
        imageInfo = db.session.query(ImageInfo).filter_by(id = imgId).one()
 
        # Create entry in database
        fileToDB = RelevantFiles(
            fileName = fileName,  
            path = os.path.abspath(newPath),
            contentDesc = data['contentDesc'],
            size = fileSize,
            suggestedReviewPlatform = data['suggestedReviewPlatform'],
            notes = data['notes'],
            users = users,
            image_info = imageInfo )

        # Add and stage for commit to database
        db.session.add(fileToDB)
        db.session.commit()
        
    def get(self, userId, caseId, deviceId, dmId, imgId):
        # Get specific file for specified image/digital media/device/case for logged in user
        if request.args.get('fileId'):
            file = db.session.query(RelevantFiles).filter_by(id = request.args.get('fileId'), userId = userId).one()

            return send_file(file.path)
        # Need file id, return 400
        else:
            return abort(400), "Need fileId as query parameter!"
    
    def post(self, userId, caseId, deviceId, dmId, imgId):
        post = "[POST FILE] "

        # Check if POST request has file part
        if 'file' not in request.files:
            print (post + 'No file in request')
            return abort(400), "No file to upload."

        newFile = request.files['file']
        print(newFile.filename)
        
        if newFile:
            # Get file name securely
            fileName = secure_filename(newFile.filename)

            # Get a new path
            newPath = os.path.join(app.config['UPLOAD_FOLDER'] + "/", fileName)
           
            print(post + "Checking for dup files...")
            # Check if file exist in directory
            tempFile = Path(newPath)
            if tempFile.is_file():
               return abort(400), "File with this name already exists!"

            # Save file to new path
            newFile.save(newPath)

            print(post + "Getting file size...")
            # Get file size, returns in bytes
            # If you want megabytes, multiple by one million
            fileSize = os.stat(UPLOAD_FOLDER + '/' + fileName).st_size
        
        # Get JSON associated with the file
        self.sendJSON(userId, imgId, request, newPath, fileName, fileSize)

        return 200

class FileMetaData(Resource):   
    def get(self, userId, caseId, deviceId, dmId, imgId):
        # Get specific file for specified image/digital media/device/case for logged in user
        if request.args.get('fileId'):
            file = db.session.query(RelevantFiles).filter_by(id = request.args.get('fileId'), userId = userId).one()

            return file.serialize
        # Get all files for specified image/digital media/device/case for logged in user
        else:
            files = db.session.query(RelevantFiles).filter_by(imageInfoId = imgId, userId = userId).all()
            return { "files_list": [file.serialize for file in files ] }
    
# Clear all contents in database
class Nuke(Resource):
    # Remove all entries for some database table
    def clearTable(self, tableName, tablePK, debugString):
        if debugString:
            print(debugString)

        db.session.query(tableName).delete()
        db.session.commit()

        # Reset the auto increment for the primary key
        db.engine.execute("ALTER SEQUENCE " + tablePK + " RESTART WITH 1;")

    def delete(self):
        nuke = "[NUKE] "

        # Remove all entries/rows/tuples starting from RelevantFiles and working backwards
        self.clearTable(RelevantFiles, "relevant_files_id_seq",
            nuke + "Clearing relevant files table...")
        self.clearTable(ImageInfo, "image_info_id_seq", 
            nuke + "Clearing image info table...")
        self.clearTable(DigitalMediaDesc, "digital_media_desc_id_seq", 
            nuke + "Clearing digital media description table...")
        self.clearTable(DeviceDesc, "device_desc_id_seq", 
            nuke + "Clearing device table...")
        self.clearTable(CaseSummary, "case_summary_id_seq", 
            nuke + "Clearing case summary table...")
        self.clearTable(Users, "users_id_seq", 
            nuke + "Clearing users table...")

        return "NUKED"

# Dashboard endpoints
api.add_resource(UserInfo,     '/evd/user')
api.add_resource(Case,         '/evd/<int:userId>/case')
api.add_resource(Device,       '/evd/<int:userId>/case/<int:caseId>/dev')
api.add_resource(Media,        '/evd/<int:userId>/case/<int:caseId>/dev/<int:deviceId>/dm')
api.add_resource(Image,        '/evd/<int:userId>/case/<int:caseId>/dev/<int:deviceId>/dm/<int:dmId>/img')
api.add_resource(File,         '/evd/<int:userId>/case/<int:caseId>/dev/<int:deviceId>/dm/<int:dmId>/img/<int:imgId>/file')
api.add_resource(FileMetaData, '/evd/<int:userId>/case/<int:caseId>/dev/<int:deviceId>/dm/<int:dmId>/img/<int:imgId>/filemd')

# Endpoint to remove all entries from all tables in the DB
api.add_resource(Nuke, '/evd/nuke')

if __name__ == "__main__":
    #app.run(host = app.run(host = 'localhost', port = 5000), debug=True)
    app.run(host = app.run(host = '129.65.100.50', port = 5000, use_debugger=True, threaded=True), debug=True)
#    app.run( host = app.run( host ='ec2-34-212-218-147.us-west-2.compute.amazonaws.com', port = 80, use_debugger=True, threaded=True), debug=True)
