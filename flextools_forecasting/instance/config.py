import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://flextools_forecasting:flextools_forecasting@db/flextools_forecasting') 
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
TESTING = True
PYTHONUNBUFFERED=True
STORAGE_LOCATION_TRACKING_API = os.environ.get('STORAGE_LOCATION_TRACKING_URI', 'http://localhost:5000/api/v1')