import json
import os
import time
import logging
from datetime import datetime

class TaskMonitor:
    def __init__(self, task_name):
        self.task_name = task_name
        self.start_time = None
        self.end_time = None
        self.monitoring_dir = '/opt/airflow/monitoring'

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def start(self):
        """Starts the timer."""
        self.start_time = time.time()

    def finish(self):
        """Stops the timer and calculates the duration."""
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        self._save_time(elapsed_time)

    def _save_time(self, elapsed_time):
        """Saves the elapsed time into a JSON file, creating or appending to an existing one."""
        # File name in the format brewery_api_dd_hh.json
        now = datetime.now()
        file_name = f"brewery_api_{now.strftime('%d_%H')}.json"
        file_path = os.path.join(self.monitoring_dir, file_name)

        # Data to be saved
        task_data = {
            "task_name": self.task_name,
            "start_time": datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(self.end_time).strftime('%Y-%m-%d %H:%M:%S'),
            "elapsed_time_seconds": elapsed_time
        }

        # Check if the file already exists for appending
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r+') as file:
                    data = json.load(file)
                    data.append(task_data)
                    file.seek(0)
                    json.dump(data, file, indent=4)
                logging.info(f"Data appended to the existing file: {file_path}")
            else:
                with open(file_path, 'w') as file:
                    json.dump([task_data], file, indent=4)
                
            logging.info(f"Task '{self.task_name}' saved successfully!")
        except Exception as e:
            logging.error(f"Error saving task '{self.task_name}': {e}")