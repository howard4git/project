from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from kafka3.admin import KafkaAdminClient, NewTopic

bootstrap_servers = 'broker:29092'
topic_name = 'users'

def create_topic():
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
    admin_client.create_topics(new_topics=[topic])

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 1),
    'retries': 0
}

dag = DAG(
    'create_topic',
    default_args=default_args,
    description='A DAG to create a Kafka topic',
    schedule_interval=None,
)

create_topic_task = PythonOperator(
    task_id='create_topic',
    python_callable=create_topic,
    dag=dag
)

create_topic_task