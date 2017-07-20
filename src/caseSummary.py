from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource

class Case(Resource):
   # Return case summary
   def get(self):
      # Get JSON data from frontend containing userId
      data = request.get_json()

      # Get a specific case for logged in user
      if (caseId = request.args.get('caseId')):
         case = CaseSummary.query.filter_by(id = caseId, 
            userId=data['userId']).all()
      # Get all cases for logged in user
      else:
         case = CaseSummary.query.filter_by(userId=data['userId']).all()

      return { "json_list": [i.serialize for i in case] }
   
   # Create a new case
   def post(self):
      # Get JSON data from frontend
      data = request.get_json()

      # Create new case object, populated with values from JSON data
      case = CaseSummary(
         id = data['id'],
         dateReceived = data['dateReceived'],
         caseNumber = data['caseNumber'],
         caseDescription = data['caseDescription'],
         deviceDesc = data['deviceDesc'],
         suspectName = data['suspectName'],
         collectionLocation = data['collectionLocation'],
         examinerNames = data['examinerNames'],
         labId = data['labId'],
         userId = data['userId'] )

      # Stage case for commit to database
      db.session.add( case )

      # Commit case to database
      db.session.commit()

      return 200
