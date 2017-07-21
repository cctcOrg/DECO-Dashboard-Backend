from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, render_template, url_for
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename
from databaseSetup import FileUpload
import os
#from databaseSetup import Overview, EvidenceSummary, MediaStatus, DeviceDetails, DigitalMediaDesc, ImagingInformation, NetworkCollectionInfo, CloudCollectionInfo, Notes  
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/dbnew'
app.debug=True
api = Api(app)
db = SQLAlchemy(app)
CORS(app)
UPLOAD_FOLDER = '/Users/jacksonkurtz/Documents/Code/CCTC/CCTC-DATABASE/Uploads'      
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class SaveFileFS(Resource):
   def post(self):
      # Get file name
      if 'file' not in request.files:
          print ('No file in request')
          return 400

      # Get JSON containing some meta data of the file
      data = request.get_json()

      newFile = request.files['file']
      print( newFile.filename )
      if newFile:
         # Get file name securely
         fileName = secure_filename(newFile.filename)
         
         # Get a new path
         newPath = os.path.join(app.config['UPLOAD_FOLDER'] + "/", fileName)
        
         # Get file size TODO: Figure out if st_size returns in MB
         fileSize = os.stat(newFile).st_size

         # Save file to new path
         newFile.save(newPath)

         # Create entry in database
         fileToDB = RelevantFiles(
           fileName = fileName,  
            path = os.path.abspath(newPath)),
            contentDesc = data["contentDesc"],
            size = fileSize,
            suggestedReviewPlatform = data["suggestedReviewPlatform"],
            notes = data["notes"] )


      # Add and stage for commit to database
      db.session.add( fileToDB )
      db.session.commit()
        
      return 200

api.add_resource( SaveFileFS, '/evd/file')

if __name__ == "__main__":
    app.run( host = app.run( host = '129.65.100.50', port = 5000), debug=True )
