from airflow import DAG
from datetime import timedelta, datetime
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator  # Updated import
from airflow.operators.python import PythonOperator
import pandas as pd
import json
import boto3
from airflow.hooks.base_hook import BaseHook
import os

def kelvin_to_fahrenheit(temp_in_kelvin):
    return (temp_in_kelvin - 273.15) * (9/5) + 32

def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_ids="extract_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp"])
    feels_like_fahrenheit = kelvin_to_fahrenheit(data["main"]["feels_like"])
    min_temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp_min"])
    max_temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    transformed_data = {
        "City": city,
        "Description": weather_description,
        "Temperature (F)": temp_fahrenheit,
        "Feels Like (F)": feels_like_fahrenheit,
        "Minimum Temp (F)": min_temp_fahrenheit,
        "Maximum Temp (F)": max_temp_fahrenheit,
        "Pressure": pressure,
        "Humidity": humidity,
        "Wind Speed": wind_speed,
        "Time of Record": time_of_record,
        "Sunrise (Local Time)": sunrise_time,
        "Sunset (Local Time)": sunset_time
    }
    
    df_data = pd.DataFrame([transformed_data])
    
    # AWS credentials from Airflow Connections
    aws_conn_id = 'aws_default'  # Ensure this is configured in Airflow
    aws_conn = BaseHook.get_connection(aws_conn_id)
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_conn.login,
        aws_secret_access_key=aws_conn.password,
        aws_session_token=aws_conn.extra_dejson.get('FwoGZXIvYXdzEAIaDLanighdSYZ6wijeXCJqAZ1jo0teZUIGGZIEStR8GDCpLRjl4sZDTlIwa5KCnFBbnmxD2Zg4N1wDKUHiq8EhZg6Ih929YKYM5g2mqM9Goek76F2iugNJsBPGWsquMJtvM4YeXnn84sWXzM11i6ZrqSMw24g17SDYPiiMgMS1BjIoN5J9ungaroNTxG8dVY2iTdN8U//Qet/pgnfgjG6H+hHP/mI/LbK/3Q==') # TOKEN
    )
    
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    file_name = f'current_weather_data_portland_{dt_string}.csv'
    
    local_file_path = f'/tmp/{file_name}'
    
    # Save DataFrame to local file first
    df_data.to_csv(local_file_path, index=False)
    
    # Upload the local file to S3
    s3_client.upload_file(local_file_path, 'weatherairflow-yml', file_name)

    # Clean up local file
    os.remove(local_file_path)

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
    description='A DAG to check if the weather API is ready and process data',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    is_weather_api_ready = HttpSensor(
        task_id='is_weather_api_ready',
        http_conn_id='weathermap_api',
        endpoint='/data/2.5/weather?q=Portland&APPID=db97ffbdec6d489dc0c7e095e650136a',#API
        mode='poke',
        timeout=20,
        poke_interval=5,
    )

    extract_weather_data = HttpOperator(
        task_id='extract_weather_data',
        http_conn_id='weathermap_api',
        endpoint='/data/2.5/weather?q=Portland&APPID=db97ffbdec6d489dc0c7e095e650136a', #API
        method='GET',
        response_filter=lambda r: json.loads(r.text),
        log_response=True,
    )

    transform_load_weather_data = PythonOperator(
        task_id='transform_load_weather_data',
        python_callable=transform_load_data,
    )

    is_weather_api_ready >> extract_weather_data >> transform_load_weather_data
