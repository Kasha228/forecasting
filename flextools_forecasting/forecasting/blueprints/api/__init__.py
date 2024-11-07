from flask import Blueprint
from flask_restx import Api


api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(
    api_blueprint, 
    version='1.0', 
    title='ForecastingAPI', 
    description='A simple API for accessing the Forecasting system.'
)