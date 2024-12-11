import requests 
from instance import config
from datetime import datetime, timedelta
from scipy.stats import expon
import numpy as np

class TransactionForecastAlgorithm:
    """
    The TransactionForecastAlgorithm class is responsible for predicting transaction forecasts

    :param algorithm: The algorithm to use for the prediction
    :type algorithm: str
    :param input_data: The input data to use for the prediction
    :type input_data: dict
    """
    @staticmethod
    def get_transaction_history(input_data):
        if input_data is None or 'transaction_history' not in input_data or not input_data.get('transaction_history'):
            try: 
                response = requests.get(f"{config.STORAGE_LOCATION_TRACKING_API}/ulRecords", json=input_data)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error getting transaction history: {e}")
        else: 
            raise NotImplementedError("This feature is not implemented yet")

    @staticmethod
    def poisson_process(event_type, input_data, horizon=1):
        """
        Predicts transaction forecast using a Poisson process (with filtering).
        """
        transaction_history = TransactionForecastAlgorithm.get_transaction_history(input_data)

        # 1. Extract timestamps and calculate inter-event times
        timestamps = []
        for entry in transaction_history:
            if event_type == 'storage' or event_type == 'both':
                timestamp = entry.get('stored_at')
                if timestamp != "None":
                    timestamps.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
            if event_type == 'retrieval' or event_type == 'both':
                timestamp = entry.get('retrieved_at')
                if timestamp != "None":
                    timestamps.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
        timestamps.sort()  # Ensure timestamps are in chronological order

        if not timestamps:
            raise ValueError("No valid records to process after cleaning data.")

        inter_event_times = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                             for i in range(1, len(timestamps))]

        # 2. Estimate the average transaction rate (lambda)
        avg_transaction_rate = len(inter_event_times) / (sum(inter_event_times) / 3600) 

        # 3. Predict transactions within the horizon
        num_events_in_horizon = np.random.poisson(avg_transaction_rate * horizon)
        predicted_times = []
        current_time = datetime.now()
        for _ in range(num_events_in_horizon):
            time_to_next_event = expon.rvs(scale=1/avg_transaction_rate)  # Time in hours
            current_time += timedelta(hours=time_to_next_event) 
            if (current_time - datetime.now()).total_seconds() <= horizon * 3600:
                predicted_times.append(str(current_time))

        return {
            "next_transaction": predicted_times, 
            "confidence_interval": None
        }

    algorithms = {
        'poisson_process': poisson_process 
    } 

    @staticmethod
    def predict(algorithm, event_type, input_data, horizon):
        """
        Predicts demand forecasts

        :param algorithm: The algorithm to use for the prediction
        :type algorithm: str
        :param input_data: The input data to use for the prediction
        :type input_data: dict
        """
        if algorithm not in TransactionForecastAlgorithm.algorithms:
            raise ValueError("Invalid algorithm")
        if event_type not in ('storage', 'retrieval', 'both'):
            raise ValueError("Invalid event type")
        return TransactionForecastAlgorithm.algorithms[algorithm](event_type, input_data, horizon)