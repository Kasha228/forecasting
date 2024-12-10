from flask import request 
from flask_restx import Namespace, Resource, fields
from forecasting.models import db, DemandForecast
from .api import request_wrapper
from forecasting.algorithms.demand import DemandForecastAlgorithm

api_namespace = Namespace('demand', description='Demand Forecast operations')

input_data_model = api_namespace.model('InputData', {
    'item_number': fields.String(description='The item number of the item', required=False),
    'item_id': fields.String(description='The item id of the item', required=False),
    'demand_history': fields.String(description='The demand history of the item', required=False)
})

demand_forecast_model = api_namespace.model('DemandForecast', {
    'id': fields.String(description='The unique identifier of the DemandForecast', readonly=True),
    'timestamp': fields.String(description='The timestamp of the DemandForecast', readonly=True),
    'input_data': fields.Nested(input_data_model, description='The input data for the forecast', required=False), 
    #TODO: define the possible types
    'forecast_type': fields.String(description='The type of the forecast', readonly=True, default="demand"),
    'algorithm': fields.String(description='The algorithm used for the forecast', required=True, default="moving_average"),
    'algorithm_version': fields.String(description='The version of the algorithm used', required=False, default="v1"),
    'prediction_horizon': fields.Integer(description='The prediction horizon of the forecast', required=False, default=10),
    'confidence_interval': fields.String(description='The confidence interval of the forecast', readonly=True),
    'predicted_demand': fields.String(description='The predicted demand data', readonly=True)
})

@api_namespace.route('/', methods=['GET', 'POST'])
class DemandForecastResource(Resource):
    @api_namespace.expect(api_namespace.parser().add_argument('id', type=str, required=False, help='The unique identifier of the DemandForecast', location='query'))
    @api_namespace.marshal_list_with(demand_forecast_model)
    @request_wrapper
    def get(self):
        """
        Returns a list of all DemandForecasts
        """
        return DemandForecast.query.all()

    @api_namespace.expect(demand_forecast_model)
    # @api_namespace.marshal_with(demand_forecast_model)
    @request_wrapper
    def post(self):
        """
        Creates a new DemandForecast
        """
        data = request.json
        forecast = DemandForecastAlgorithm().predict(data['algorithm'], data.get('input_data'))
        forecast_data = DemandForecast(
            input_data=data.get('input_data', None),
            forecast_type='demand',
            algorithm=data['algorithm'],
            algorithm_version=data.get('algorithm_version', "v1"),
            prediction_horizon=data['prediction_horizon'],
            confidence_interval=data.get('confidence_interval'),
            predicted_demand=forecast
        )
        db.session.add(forecast_data)
        db.session.commit()
        db_forecast = DemandForecast.query.get(forecast_data.id)
        return db_forecast.to_dict()