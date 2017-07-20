from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource

class Case(Resource):
   def get(self):
      

   def post(self):
      # Get JSON data from frontend
      data = request.get_json()
      
      # Create new case object, populated with values from JSON data
      case = CaseSummary(
         caseId = data['id'],
         caseDesc = data['caseDesc'],
         suspectName = data['suspectName'],
         outsideAgencyNumber = data['outsideAgencyNumber'],
         collectionLocation = data['collectionLocation'],
         examinerName = data['examinerName'],
         dateReceived = data['dateReceived'],
         labId = data['labId'],
         storageLocation = data['storageLocation'] )

      # Stage case for commit to database
      db.session.add( case )

      # Commit case to database
      db.session.commit()

      return 200
         
      
