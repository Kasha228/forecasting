from flask import Blueprint
from flask_restx import Api

from .transaction import api_namespace as transaction_namespace

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(
    api_blueprint, 
    version='1.0', 
    title='ForecastingAPI', 
    description='A simple API for accessing the Forecasting system.'
)

api.add_namespace(transaction_namespace)