import requests 
from instance import config
from datetime import datetime, timedelta, timezone
from scipy.stats import expon
import numpy as np
from enum import Enum

class AlgorithmType(str, Enum):
    POISSON_PROCESS = 'poisson_process'
    EXPONENTIAL_SMOOTHING = 'exponential_smoothing'

class TransactionForecastAlgorithm:
    """
    The TransactionForecastAlgorithm class is responsible for predicting transaction forecasts

    :param algorithm: The algorithm to use for the prediction
    :type algorithm: str
    :param input_data: The input data to use for the prediction
    :type input_data: dict
    """
    @staticmethod
    def get_transaction_history(input_data, event_type):
        if input_data is None or 'transaction_history' not in input_data or not input_data.get('transaction_history'):
            try: 
                response = requests.get(f"{config.STORAGE_LOCATION_TRACKING_API}/ulRecords", json=input_data)
                response.raise_for_status()
                transaction_history = response.json()
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error getting transaction history: {e}")
        else: 
            raise NotImplementedError("This feature is not implemented yet")
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
        return timestamps

    @staticmethod
    def poisson_process(input_data, event_type, horizon=1):
        """
        Predicts transaction forecast using a Poisson process (with filtering).
        """
        timestamps = TransactionForecastAlgorithm.get_transaction_history(input_data, event_type)
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

    @staticmethod
    def exponential_smoothing(input_data, event_type, horizon=1):
        """
        Predicts transaction forecast using exponential smoothing.

        :param input_data: Input data containing transaction history and alpha
        :param event_type: Type of event (storage, retrieval, both)
        :param horizon: Prediction horizon in hours
        :param alpha: Smoothing factor (between 0 and 1)
        """
        timestamps = TransactionForecastAlgorithm.get_transaction_history(input_data, event_type)
        if not all(timestamp.tzinfo == timestamps[0].tzinfo for timestamp in timestamps):
            raise ValueError("Timestamps have inconsistent time zone information.")
        alpha = 0.2
        if input_data is not None:
            alpha = input_data.get('alpha', 0.2)

        # Calculate smoothed timestamps
        smoothed_timestamps = []
        smoothed_timestamps.append(timestamps[0])  # Initialize with the first timestamp

        for i in range(1, len(timestamps)):
            # Calculate the difference between timestamps as seconds
            time_diff_seconds = (timestamps[i] - timestamps[i-1]).total_seconds() 
            # Calculate the smoothed time difference
            smoothed_time_diff_seconds = alpha * time_diff_seconds + (1 - alpha) * (smoothed_timestamps[i-1] - smoothed_timestamps[i-2]).total_seconds() 
            smoothed_timestamps.append(smoothed_timestamps[i-1] + timedelta(seconds=smoothed_time_diff_seconds))

        # Predict next timestamps
        predicted_times = []
        current_time = datetime.now(timezone.utc)
        while (current_time - smoothed_timestamps[-1]).total_seconds() <= horizon * 3600:
            time_to_next_event = (smoothed_timestamps[-1] - smoothed_timestamps[-2]).total_seconds()
            current_time += timedelta(seconds=time_to_next_event)
            predicted_times.append(str(current_time))

        return {
            "next_transaction": predicted_times,
            "confidence_interval": None  # Implement if needed
        }


    algorithms = {
        'poisson_process': poisson_process, 
        'exponential_smoothing': exponential_smoothing
    } 

    @staticmethod
    def predict(algorithm: AlgorithmType, input_data, event_type, horizon):
        """
        Predicts transaction forecasts using the specified algorithm.

        :param algorithm: The algorithm to use for the prediction. Options are 'poisson_process' or 'exponential_smoothing'.
        :type algorithm: AlgorithmType
        :param input_data: The input data to use for the prediction.
        :type input_data: dict
        :param event_type: Type of event ('storage', 'retrieval', or 'both').
        :type event_type: str
        :param horizon: Prediction horizon.
        :type horizon: int
        :return: Prediction results.
        :rtype: dict
        """
        if algorithm not in TransactionForecastAlgorithm.algorithms:
            raise ValueError("Invalid algorithm")
        if event_type not in ('storage', 'retrieval', 'both'):
            raise ValueError("Invalid event type")
        return TransactionForecastAlgorithm.algorithms[algorithm](input_data, event_type, horizon)