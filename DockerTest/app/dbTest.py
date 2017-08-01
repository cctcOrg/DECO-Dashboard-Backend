from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseSetup import Base, Users

engine = create_engine( 'postgresql://cctc_user:CampSLOcctc@dashboard.chxgxe8hajtr.us-west-1.rds.amazonaws.com:5432/dashboarddb' )
Base.metadata.bind = engine
DBSession = sessionmaker( bind = engine )
session = DBSession()

users = Users( email = 'test@gmail.com', lastName = 'Kurtz', firstName = 'Jackson' )
session.add( users )
session.commit()
