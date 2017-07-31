from flask import Flask
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
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/dashboarddb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cctc_user:cctc@localhost/newdb'
app.debug=True
api = Api(app)
db = SQLAlchemy(app)
CORS(app)
#UPLOAD_FOLDER = '/Users/jacksonkurtz/Documents/Code/CCTC/DashboardBackend/Uploads'     
UPLOAD_FOLDER = '/srv/http/DigitalEvidenceCollection/Backend/Uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class UserInfo(Resource):
  # create a new user 
    def post(self):
        var post = "[POST USER] "
        print(post + "Getting data from JSON...")

        data = request.get_json()

        print(post + "Creating row for DB insertion...")
        users = Users( 
            email = data['email'],
            lastName = data['lastName'],
            firstName = data['firstName'] )

        print(post + "Inserting into DB...")
        #stage and commit to database
        db.session.add( users)
        db.session.commit()

        print(post + "RETURNING 200")
        return 200

    def get(self):
        #query User table by email 
        info = db.session.query(Users).filter_by(email = request.args.get('email')).first()
        return jsonify( id=info.id, email=info.email, firstName=info.firstName, lastName=info.lastName)


class Case(Resource):
   # Return case summary
    def get(self, userId):
        # Get JSON data from frontend containing userId

        # Get a specific case for logged in user
        if (request.args.get('caseId')):
            case = db.session.query(CaseSummary).filter_by(id = request.args.get('caseId'), userId=userId).one()
            return case.serialize
        # Get all cases for logged in user
        else:
            case = db.session.query(CaseSummary).filter_by(userId=userId).all()
            return { "json_list": [i.serialize for i in case] }
   
    # Create a new case
    def post(self, userId):
        # Get JSON data from frontend
        data = request.get_json()

        # Create new case object, populated with values from JSON data
        user = db.session.query(Users).filter_by( id = userId ).one()
        case = CaseSummary(
            dateReceived = data['dateReceived'],
            caseNumber = data['caseNumber'],
            caseDescription = data['caseDescription'],
            suspectName = data['suspectName'],
            collectionLocation = data['collectionLocation'],
            examinerNames = data['examinerNames'],
            labId = data['labId'],
            users = user )

        # Stage case for commit to database
        db.session.add( case )
        # Commit case to database
        db.session.commit()
        return 200

class Device( Resource):
    def get(self, userId):
            data = request.get_json() 
            info = db.session.query(DeviceDesc).filter_by(caseSummaryId = request.args.get('caseId')).all()
            return { "json_list": [i.serialize for i in info] }

    def post( self, userId ):
        data = request.get_json()
        users = db.session.query(Users).filter_by( id = userId).one()
        case_summary = db.session.query(CaseSummary).filter_by(id = request.args.get('caseId') ).one()
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
                case_summary = case_summary
                )
        db.session.add( deviceDesc )
        db.session.commit()
        return 200

class Media(Resource):
    def post(self, userId):
        data = request.get_json()
        users = db.session.query( Users).filter_by( id = userId).one()
        deviceDesc = db.session.query( DeviceDesc ).filter_by( id = request.args.get('deviceId')).one()
        media = DigitalMediaDesc (
                storageId = data['storageId'],
                make = data['make'],
                model = data['model'],
                serialNumber = data['serialNumber'],
                capacity = data['capacity'],
                users = users,
                device_desc = deviceDesc )
        db.session.add( media )
        db.session.commit()
        return 200
 
    def get(self, userId):
        media = db.session.query( DigitalMediaDesc ).filter_by(deviceDescId = request.args.get('deviceId')).all()
        return { "digital media list": [i.serialize for i in media] }

class Image( Resource):
    def get(self, userId):
        info = db.session.query(ImageInfo).filter_by(digitalMediaDescId=request.args.get('mediaId')).all()
        return { "json_list": [i.serialize for i in info ] }

    def post( self, userId ):
        data = request.get_json()
        users = db.session.query(Users).filter_by( id = userId).one()
        digital_media_desc = db.session.query(DigitalMediaDesc).filter_by( id = request.args.get('mediaId')).one()
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
                users=users,
                digital_media_desc = digital_media_desc 
                )
        db.session.add( imageInfo )
        db.session.commit()
        return 200


class SaveFileFS(Resource):   
    def post(self, userId):
        # Get file name
        if 'file' not in request.files:
            print ('No file in request')
            return 400
        users = db.session.query(Users).filter_by( id = userId).one()
        image_info = db.session.query(ImageInfo).filter_by( id = request.args.get('imageId')).one()
 
      # Get JSON containing some meta data of the file
        data = request.form
        print ( "request.form: ", request.form )
        print ("data dict: ", data)
        newFile = request.files['file']
        print( newFile.filename )
        if newFile:
        # Get file name securely
            fileName = secure_filename(newFile.filename)

            # Get a new path
            newPath = os.path.join(app.config['UPLOAD_FOLDER'] + "/", fileName)

            # Save file to new path
            newFile.save(newPath)

            # Get file size TODO: Figure out if st_size returns in MB
            fileSize = os.stat(UPLOAD_FOLDER + '/' + fileName).st_size

            # Create entry in database
            fileToDB = RelevantFiles(
                fileName = fileName,  
                path = os.path.abspath(newPath),
                contentDesc = data["contentDesc"],
                size = fileSize,
                suggestedReviewPlatform = data["suggestedReviewPlatform"],
                notes = data["notes"],
                users = users,
                image_info = image_info
                )


      # Add and stage for commit to database
        db.session.add( fileToDB )
        db.session.commit()

        return 200

# Clear all contents in database
class Nuke(Resource):
    def delete(self):
       # Remove all entries/rows/tuples starting from RelevantFiles and working backwards
       # Work backwards to avoid violating foreign key constraints
       db.RelevantFiles.query.delete()
       db.ImageInfo.query.delete()
       db.DigitalMediaDesc.query.delete()
       db.DeviceDesc.query.delete()
       db.CaseSummary.query.delete()
       db.Users.query.delete()

       return "NUKED"

api.add_resource( UserInfo, '/evd/user')
api.add_resource( Case, '/evd/<int:userId>/case')
api.add_resource( Device, '/evd/<int:userId>/dev')
api.add_resource( Media, '/evd/<int:userId>/dm')
api.add_resource( Image, '/evd/<int:userId>/img')
api.add_resource( SaveFileFS, '/evd/<int:userId>/file')

# Endpoint to remove all entries from all tables in the DB
api.add_resource( Nuke, '/evd/nuke')

if __name__ == "__main__":
    #app.run( host = app.run( host = '129.65.247.21', port = 5000), debug=True )
    app.run( host = app.run( host = '129.65.100.50', port = 5000, use_debugger=True, threaded=True), debug=True )
