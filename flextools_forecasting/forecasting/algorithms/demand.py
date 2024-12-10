import requests 
from instance import config

class DemandForecastAlgorithm:
    """
    The DemandForecastAlgorithm class is responsible for predicting demand forecasts

    :param algorithm: The algorithm to use for the prediction
    :type algorithm: str
    :param input_data: The input data to use for the prediction
    :type input_data: dict
    """
    @staticmethod
    def get_demand_history(input_data):
        if 'demand_history' not in input_data or not input_data.get('demand_history'):
            try: 
                if 'item_number' in input_data:
                    response = requests.get(f"{config.STORAGE_LOCATION_TRACKING_API}/?item_number={input_data['item_number']}")
                elif 'item_id' in input_data:
                    response = requests.get(f"{config.STORAGE_LOCATION_TRACKING_API}/?item_id={input_data['item_id']}")
                else:
                    response = requests.post(f"{config.STORAGE_LOCATION_TRACKING_API}/", json=input_data)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error getting demand history: {e}")
        else: 
            raise NotImplementedError("This feature is not implemented yet")

    def moving_average(input_data):
        """
        Predicts demand forecasts using the moving average algorithm

        :param input_data: The input data to use for the prediction
        :type input_data: dict
        """
        demand_history = DemandForecastAlgorithm.get_demand_history(input_data)
        return {"forecast": demand_history, "confidence_interval": None}


    algorithms = {
        'moving_average': moving_average
    } 

    @staticmethod
    def predict(algorithm, input_data):
        """
        Predicts demand forecasts

        :param algorithm: The algorithm to use for the prediction
        :type algorithm: str
        :param input_data: The input data to use for the prediction
        :type input_data: dict
        """
        if algorithm not in DemandForecastAlgorithm.algorithms:
            raise ValueError("Invalid algorithm")
        return DemandForecastAlgorithm.algorithms[algorithm](input_data)