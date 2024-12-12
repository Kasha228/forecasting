from flask import request 
from flask_restx import Namespace, Resource, fields
from forecasting.models import db, TransactionForecast 
from .api import request_wrapper
from forecasting.algorithms.transaction import TransactionForecastAlgorithm

api_namespace = Namespace('transaction', description='Transaction Forecast operations')

input_data_model = api_namespace.model('InputData', {
    'transaction_history': fields.String(description='The Transaction history', required=False)
})

prediction_model = api_namespace.model('Prediction', {
    'next_transaction': fields.String(description='The next transaction', required=True),
    'confidence_interval': fields.String(description='The confidence interval of the forecast', required=False)
})

transaction_forecast_model = api_namespace.model('TransactionForecast', {
    'id': fields.String(description='The unique identifier of the TransactionForecast', readonly=True),
    'timestamp': fields.String(description='The timestamp of the TransactionForecast', readonly=True),
    'input_data': fields.Nested(input_data_model, description='The input data for the forecast', required=False),
    'forecast_type': fields.String(description='The type of the forecast', readonly=True, default="transaction"),
    'algorithm': fields.String(
        description='The algorithm used for the forecast',
        required=True,
        default="poisson_process",
        enum=['poisson_process', 'exponential_smoothing']
    ),
    'algorithm_version': fields.String(description='The version of the algorithm used', readonly=False, default="v1"),
    'prediction_horizon': fields.Integer(description='The prediction horizon of the forecast', readonly=False, default=10),
    'predicted_output': fields.Nested(prediction_model, description='The predicted output of the forecast', readonly=True),
    'event_type': fields.String(
        description='The type of event to forecast',
        required=True,
        default="both",
        enum=['storage', 'retrieval', 'both']
    )
})

@api_namespace.route('/', methods=['GET', 'POST'])
class TransactionForecastResource(Resource):
    @api_namespace.expect(api_namespace.parser().add_argument('id', type=str, required=False, help='The unique identifier of the Transaction Forecast', location='query'))
    @api_namespace.marshal_list_with(transaction_forecast_model)
    @request_wrapper
    def get(self):
        """
        Returns a list of all DemandForecasts
        """
        return TransactionForecast.query.all()

    @api_namespace.expect(transaction_forecast_model)
    # @api_namespace.marshal_with(transaction_forecast_model)
    @request_wrapper
    def post(self):
        """
        Creates a new TransactionForecast 
        """
        data = request.json
        forecast = TransactionForecastAlgorithm().predict(data['algorithm'], data.get('input_data'), data.get('event_type'), data.get('prediction_horizon'))
        forecast_data = TransactionForecast(
            input_data=data.get('input_data'),
            algorithm=data['algorithm'],
            event_type=data['event_type'],
            predicted_output=forecast  
        )
        db.session.add(forecast_data)
        db.session.commit()
        db_forecast = TransactionForecast.query.get(forecast_data.id)
        return db_forecast.to_dict()