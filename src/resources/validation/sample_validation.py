import json
from collections import Counter
from glob import glob
from pathlib import Path
import logging
from resources.brew_api.brewapi_bronze import BreweryRequestsApi
from resources.utils.utils import log_header

config_path = Path("src/resources/utils/configs.json")

with config_path.open('r') as config_file:
    config = json.load(config_file)

class Ingestion_validation:
    _bronze_path_file = Path(config['paths']['bronze'])


    # Schema definition for the validation process
    _expected_schema = {
        "id": str,
        "name": str,
        "brewery_type": str,
        "address_1": (str, type(None)),
        "address_2": (str, type(None)),
        "address_3": (str, type(None)),
        "city": str,
        "state_province": str,
        "postal_code": str,
        "country": str,
        "longitude": (str, type(None)),
        "latitude": (str, type(None)),
        "phone": (str, type(None)),
        "website_url": (str, type(None)),
        "state": str,
        "street": (str, type(None))
    }

    def _validate_files_numbers(self, expected_total_responses: int) -> None:
        
        total_responses = 0
        responses_per_file = []

        # var aux for airflow branch [data quality]
        var_validation_ingestion_1 = 0

        msg = "BEGINNING DATA INGESTION [# & TYPE] VALIDATION"
        log_header(msg)

        logging.info('[VALIDATION] -> STARTING [#] VALIDATION')

        files = sorted(list(glob(str(self._bronze_path_file / '*'))))
        for num, directory in enumerate(files):
            with open(directory) as json_file:
                data = json.load(json_file)
                responses_per_file.append(len(data))
                total_responses += len(data)
        try:
            if total_responses != expected_total_responses:
                var_validation_ingestion_1 = 1
                raise ValueError(f'Expected total_responses {expected_total_responses}, but got {total_responses}')
            
        except  ValueError as e:
            print(f'Expected total_responses {expected_total_responses}, but got {total_responses}')

        
        responses_per_file = Counter(responses_per_file)
        responses_per_file = [
            f'{responses_per_file.get(n)} {"FILE" if responses_per_file.get(n) == 1 else "FILES"} WITH {n} BREWERIES'
            for n in responses_per_file.keys()
        ]

        logging.info(
            f'[VALIDATION] -> TOTAL NUMBER OF FILES SAVED: {len(files)}\n' +
            f"\n".join(responses_per_file) +
            f'\nTOTAL NUMBER OF BREWERIES: {total_responses}'
        )
        logging.info('[VALIDATION] -> [#] VALIDATION FINISHED')
        return var_validation_ingestion_1
    
    def _validate_files_types(self) -> None:
        logging.info('[VALIDATION] ->STARTING [TYPE] VALIDATION')

        # var aux for airflow branch [data quality]
        var_validation_ingestion_2 = 0
        
        files = sorted(list(glob(str(self._bronze_path_file / '*'))))

        for directory in files:
            with open(directory) as json_file:
                data = json.load(json_file)

                # Valida a tipagem de cada registro no arquivo
                for idx, record in enumerate(data):
                    for key, expected_type in self._expected_schema.items():
                        try:
                            if key not in record:
                                var_validation_ingestion_2 = 1
                                raise ValueError(f'Missing key "{key}" in file "{directory}", record index {idx}')

                            if not isinstance(record[key], expected_type):
                                var_validation_ingestion_2 = 1
                                raise TypeError(f'Key "{key}" in file "{directory}", record index {idx} expected type {expected_type}, but got {type(record[key])}')
                        except (ValueError, TypeError) as e:
                            logging.error(f'[VALIDATION] -> [TYPE] ERROR: {e}')
                            

        logging.info('[VALIDATION] -> [TYPE] VALIDATION FINISHED')
        msg = '[VALIDATION] -> FILE VALIDATION FINISHED'
        log_header(msg)

        return var_validation_ingestion_2

    
    def validation_execute(self):
        page_data = BreweryRequestsApi()._total_pages()
        total_records_api = page_data['total_records']
        var_validation_ingestion_1 = self._validate_files_numbers(expected_total_responses=total_records_api)
        var_validation_ingestion_2 = self._validate_files_types()
        
        return var_validation_ingestion_1 + var_validation_ingestion_2