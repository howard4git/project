from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from kafka3 import KafkaProducer

bootstrap_servers = 'localhost:9092'
topic = 'howard'
message = b'Hello, Kafka!'

def send_msg_to_kafka():
    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms = 5000)
    producer.send(topic, value=message)
    producer.close()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 1),
    'retries': 1
}

dag = DAG(
    'send_msg_to_kafka',
    default_args=default_args,
    description='test send msg to kafka',
    schedule_interval='@daily',
    catchup=False
)

send_msg_task = PythonOperator(
    task_id='send_msg_to_kafka',
    python_callable=send_msg_to_kafka,
    dag=dag
)

send_msg_task
