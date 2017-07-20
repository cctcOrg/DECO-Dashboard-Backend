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

class Media(Resource):
    def post(self):
      data = request.get_json()
      media = DigitalMediaDesc (
            storageId = data['storageId'],
            make = data['make'],
            model = data['model'],
            serialNumber = data['serialNumber'],
            capacity = data['capacity'] 
            users = users
            deviceDesc = device_description )
      db.session.add( media )
      db.session.commit()
 
    def get(self):
      data = request.get_json();
      media = db.session.query( DigitalMediaDesc ).filter_by(deviceDescId = data['deviceDescId']).all()
      return { "digital media list": [i.serialize for i in media] }

api.add_resource( UserInfo, '/evd/user')
api.add_resource( Media, '/evd/media')
api.add_resource( Form, '/evd/form')
api.add_resource( First, '/evd/first')
api.add_resource( SaveFileFS, '/evd/upload')

if __name__ == "__main__":
    app.run( host = app.run( host = '129.65.247.21', port = 5000), debug=True )
    #app.run( host = app.run( host = '129.65.100.50', port = 5000), debug=True )
