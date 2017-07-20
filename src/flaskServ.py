from flask import Flask
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Response, jsonify, request, redirect, render_template, url_for
from sqlalchemy import create_engine
from databaseSetup import FileUpload, User, Overview, EvidenceSummary, MediaStatus, DeviceDetails, DigitalMediaDesc, ImagingInformation, NetworkCollectionInfo, CloudCollectionInfo, Notes  
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/dbnew'
app.debug=True
api = Api(app)
db = SQLAlchemy(app)
CORS(app)
UPLOAD_FOLDER = '/Users/jacksonkurtz/Documents/Code/CCTC/CCTC-DATABASE/Uploads'      
#UPLOAD_FOLDER = '/srv/http/CCTC-DATABASE/Uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class UserInfo(Resource):
  # create a new user 
  def post(self):
    data = request.get_json()
    user = User( 
        email = data['email'],
        lastName = data['lastName'],
        firstName = data['firstName'] )
    #stage and commit to database
    db.session.add( user)
    db.session.commit()
    return 200

  def get(self):
    #query User table by email 
    info = db.session.query(User).filter_by(email = request.args.get('email')).first()
    #return Response( json.dumps(info.id, info.firstName), mimetype='application/json' )
    return jsonify( id=info.id, email=info.email, firstName=info.firstName, lastName=info.lastName)

class Form(Resource):
    def post(self):
        print( "request: ", request)
        data = request.get_json()
        print( "data posted: ", data )
        user = db.session.query(User).filter_by( id = data['userId']).one() 
        print( "user id: ", user.id)
        overview = Overview( 
                deviceDesc = data['deviceDesc'], 
                imageName=data['imageName'], 
                primaryStorageMediaId=data['primaryStorageMediaId'], 
                backupStorageMediaId=data['backupStorageMediaId'],
                dateOfSubmittal = datetime.datetime.now(),
                user = user)
        evidenceSummary = EvidenceSummary(
                dateOfCollections = data['dateOfCollections'], 
                caseNumber = data['caseNumber'], 
                subjectName = data['subjectName'], 
                examinerName = data['examinerName'], 
                collectionLocation = data['collectionLocation'],
                typeOfCollection = data['typeOfCollection'], 
                overview = overview)
        mediaStatus = MediaStatus(
                mediaStatus = data['mediaStatus'], 
                overview = overview, 
                evidence_summary = evidenceSummary)
        deviceDetails = DeviceDetails( 
                make = data['make'], 
                model = data['model'],
                serialNumber = data['serialNumber'],
                deviceStatus = data['deviceStatus'],
                shutDownMethod = data['shutDownMethod'], 
                systemDateTime = data['systemDateTime'],
                localDateTime = data['localDateTime'],
                overview = overview)
        digitalMediaDesc = DigitalMediaDesc(
                dmdMake = data['dmdMake'],
                dmdModel = data['dmdModel'],
                oemStorageCapacity = data['oemStorageCapacity'],
                dmdSerialNumber = data['dmdSerialNumber'],
                internalSerialNumber = data['internalSerialNumber'],
                interface = data['interface'],
                mediaType = data['mediaType'],
                overview = overview)
        # Grab data from JSON relevant to ImagingInformation and put into database
        imageinfo = ImagingInformation( 
                writeBlockMethod = data['writeBlockMethod'], 
                imagingTools = data['imagingTools'], 
                format = data['format'],
                overview = overview)

        # Grab data from JSON relevant to ImagingInformation and put into database
        netinfo = NetworkCollectionInfo( 
                connection = data['connection'], 
                collectionType = data['collectionType'], 
                path = data['path'],
                overview = overview)
        cloudinfo = CloudCollectionInfo( 
                toolUsed = data['toolUsed'],
                userAccountInfo = data['userAccountInfo'],
                overview = overview)
        notes = Notes( 
                postCollection = data['postCollection'],
                generalNotes = data['generalNotes'],
                overview = overview)

        # add and commit to database
    
        # Add and stage for commit to database
        db.session.add( user)
        db.session.add( overview )
        db.session.add( evidenceSummary )
        db.session.add( deviceDetails )
        db.session.add( mediaStatus )
        db.session.add( imageinfo )
        db.session.add( netinfo )
        db.session.add( digitalMediaDesc)
        db.session.add( cloudinfo )
        db.session.add( notes )

        db.session.commit()
        return 200

    def options(self):
        return { 'Allow': 'POST'}, 200

    def get( self ):
        if request.args.get( 'userId'):
            forms = db.session.query( Overview ).filter_by( userId = request.args.get('userId')).all()
            return { "json_list": [i.serialize for i in forms] }
        if request.args.get( 'id' ):
            info = db.session.query( Overview ).filter_by( id = request.args.get('id')).one()
            return {  info.evidenceSummary.serialize  }

class SaveFileFS(Resource):
    def post(self):
        # Get file name
        if 'file' not in request.files:
            print ('No file in request')
            return 400
        newFile = request.files['file']
        print( newFile.filename )
        if newFile:
            # Get file name securely
            fileName = secure_filename(newFile.filename)

            # Get a new path
            newPath = os.path.join(app.config['UPLOAD_FOLDER'] + "/", fileName)

            # Save file to new path
            newFile.save(newPath)
            # Create entry in database
            fileToDB = FileUpload(
                fileName = fileName, 
                pathToFile = os.path.abspath(newPath),
                dateOfUpload = datetime.datetime.now() )

            # Add and stage for commit to database
            db.session.add( fileToDB )
            db.session.commit()
            return 200

class First(Resource):
    def post(self):
        print( "request: ", request)
        data = request.get_json()
        print( "data posted: ", data )
        overview = Overview( deviceDesc = data['deviceDesc'], imageName=data['imageName'], primaryStorageMediaId=data['primaryStorageMediaId'], backupStorageMediaId=data['backupStorageMediaId'] )
        db.session.add( overview )
        db.session.commit()
        return 200

api.add_resource( UserInfo, '/evd/user')
api.add_resource( Form, '/evd/form')
api.add_resource( First, '/evd/first')
api.add_resource( SaveFileFS, '/evd/upload')

if __name__ == "__main__":
    app.run( host = app.run( host = '129.65.247.21', port = 5000), debug=True )
    #app.run( host = app.run( host = '129.65.100.50', port = 5000), debug=True )
