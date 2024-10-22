from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from viz_data_deprecated import execute_viz_data_bronze, execute_viz_data_silver, execute_viz_data_gold
import pendulum

# Only for dev purposes


with DAG(
    dag_id='dag_vizualization',
    schedule_interval='10 15 * * *',
    start_date=pendulum.datetime(2024, 2, 10, tz='America/Sao_Paulo'),
    catchup=False,
    tags=['BreweryDelta']
) as dag:
     
     viz_data_task_bronze = PythonOperator(
        task_id='brew_data_vizualization_bronze',
        python_callable=execute_viz_data_bronze
    )
     
     viz_data_task_silver = PythonOperator(
        task_id='brew_data_vizualization_silver',
        python_callable=execute_viz_data_silver
    )
    
     viz_data_task_gold = PythonOperator(
        task_id='brew_data_vizualization_gold',
        python_callable=execute_viz_data_gold
    )
     
viz_data_task_bronze >> viz_data_task_silver >> viz_data_task_gold