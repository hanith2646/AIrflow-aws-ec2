from airflow import DAG
from datetime import timedelta, datetime
from airflow.providers.http.sensors.http import HttpSensor

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 8),
    'email': ['myemail@domain.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

# Define the DAG
with DAG(
    'weather_dag',
    default_args=default_args,
    description='A DAG to check if the weather API is ready',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Define the HttpSensor task
    is_weather_api_ready = HttpSensor(
        task_id='is_weather_api_ready',
        http_conn_id='weathermap_api',  # Ensure this connection is defined in Airflow
        endpoint='/data/2.5/weather?q=Portland&APPID=db97ffbdec6d489dc0c7e095e650136a',
        mode='poke',  # or 'reschedule', depending on your use case
        timeout=20,
        poke_interval=5,
    )

    # Since no other tasks are defined, we end here
    # If you had more tasks, you would define them and set dependencies here
