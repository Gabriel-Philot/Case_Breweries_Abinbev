from resources.brew_api.brewapi_bronze import BreweryRequestsApi
from resources.utils.monitor import TaskMonitor

def brewery_api_to_bronze():
    monitor = TaskMonitor("api_ingestion_to_bronze")
    monitor.start()
    BreweryRequestsApi().extract_data()
    monitor.finish()

if __name__ == "__main__":
    brewery_api_to_bronze()
