from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
import pendulum
from api_to_bronze import brewery_api_to_bronze
from validation import raw_files_validation, branch_check, simulated_branch
from bronze_to_silver import execute_bronze_to_silver
from silver_to_gold import execute_silver_to_gold


with DAG(
    dag_id='BreweryDelta',
    schedule_interval='10 15 * * *',
    start_date=pendulum.datetime(2024, 2, 10, tz='America/Sao_Paulo'),
    catchup=False,
    tags=['BreweryDelta']
) as dag:

    brew_extract_task = PythonOperator(
        task_id='brew_extract_api',
        python_callable=brewery_api_to_bronze
    )

    brew_ingestion_validation_task = PythonOperator(
        task_id='brew_ingestion_validation',
        python_callable=raw_files_validation,
        provide_context=True,
    )

    branch_task = BranchPythonOperator(
    task_id = "branch_check_ingestion",
    python_callable = branch_check,
    provide_context=True,
    )

    simulation_task = PythonOperator(
        task_id = "simulated_action",
        python_callable = simulated_branch
    )

    bronze_to_silver_task = PythonOperator(
        task_id = "bronze_to_silver",
        python_callable = execute_bronze_to_silver
    )

    silver_to_gold_task = PythonOperator(
        task_id = "silver_to_gold",
        python_callable = execute_silver_to_gold
    )


    brew_extract_task >> brew_ingestion_validation_task >> branch_task
    branch_task >> [bronze_to_silver_task, simulation_task]
    bronze_to_silver_task >> silver_to_gold_task
