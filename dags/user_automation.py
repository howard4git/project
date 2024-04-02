from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
from kafka3 import KafkaProducer, KafkaConsumer
from kafka3.errors import kafka_errors
from airflow.utils.task_group import TaskGroup
import requests
import logging
import psycopg2
from airflow.models import Variable
import sys


##DB host should put the db container name instead of localhost !!! ##
## Setting Enviroment Variable ##
Variable.set("db_host", "project-postgres-1")
Variable.set("db_hostname", "postgres")
Variable.set("db_port", "5432")
Variable.set("db_name", "postgres")
Variable.set("db_user", "airflow")
Variable.set("db_password", "airflow")
Variable.set("broker", "broker:29092")
Variable.set("group_id", "test-consumer-group")

## Getting Enviroment Variable ##
db_host = Variable.get("db_host")
db_hostname = Variable.get("db_hostname")
db_port = Variable.get("db_port")
db_name = Variable.get("db_name")
db_user = Variable.get("db_user")
db_password = Variable.get("db_password")
broker = Variable.get("broker")
group_id = Variable.get("group_id")



default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 2)
}


def get_data():
    res = requests.get('https://randomuser.me/api/')
    res = res.json()
    res = res['results'][0]
    return res


def format_data(res):
    data = {}
    location = res['location']
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {str(location['street']['name'])}" \
                      f"{location['city']} {location['state']} {location['country']}"
    data['postcode'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']

    return data


def streaming_data():
    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    batch_size = 0

    while True:
        if batch_size == 100:
            break
        try:
            res = get_data()
            res = format_data(res)
            producer.send('user_created', json.dumps(res).encode('utf-8'))
            logging.info(f'data sent: {res}')

        except Exception as e:
            logging.error(f'An error occurred: {e} ')
            continue
        batch_size += 1

def check_db_exist():
    conn = psycopg2.connect(
        dbname='postgres',
        user='airflow',
        password=db_password,
        host=db_host,
        port=db_port
    )

    # Create instance
    cursor = conn.cursor()
    # Check if table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_info')")
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        # Create table if not exists
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS user_info ("
            "id SERIAL PRIMARY KEY,"
            "first_name VARCHAR(255),"
            "last_name VARCHAR(255),"
            "gender VARCHAR(255),"
            "address VARCHAR(255),"
            "postcode VARCHAR(255),"
            "email VARCHAR(255),"
            "username VARCHAR(255),"
            "registered_date VARCHAR(255),"
            "phone VARCHAR(255),"
            "picture VARCHAR(255)"
            ")"
        )
        conn.commit()
        return "Table user_info created"
    return "Table user_info already exists"



## Inner call used only
def consume_msg_from_kafka():

    topic = "user_created"
    # Create KafkaConsumer Instance
    consumer = KafkaConsumer(topic,
                             group_id=group_id,
                             bootstrap_servers=broker,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True
                             )

    consumed_msgs = []
    max_msgs_to_consume = 300
    try:
        for message in consumer:
            if message is None:
                continue
            if message.value is None:
                if message.error.code == kafka_errors._PARTITION_EOF:
                    # End of partition, continue polling
                    continue
                else:
                    raise kafka_errors(message.error())
            else:
                # Process the message
                print(f"Received message: {message.value}")
                consumed_msg = json.loads(message.value)
                consumed_msgs.append(consumed_msg)
                if len(consumed_msgs) >= max_msgs_to_consume:
                    break
    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        consumer.close()
    return consumed_msgs


def consume_and_store_data():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_hostname,
        port=db_port
    )
    kafka_msg = consume_msg_from_kafka()
    cursor = conn.cursor()
    print(f"Kafka message---->: {kafka_msg}")

    for i in range(len(kafka_msg)):
        # Insert to SQL
        cursor.execute(
            "INSERT INTO user_info (id, first_name, last_name, gender, address, postcode, email, username, registered_date, phone, picture) \
             VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (kafka_msg[i]['first_name'], kafka_msg[i]['last_name'], kafka_msg[i]['gender'], kafka_msg[i]['address'],
             kafka_msg[i]['postcode'], kafka_msg[i]['email'],
             kafka_msg[i]['username'], kafka_msg[i]['registered_date'], kafka_msg[i]['phone'], kafka_msg[i]['picture'])
        )

        # submit & close
        conn.commit()

    cursor.close()
    conn.close()

    return "Success"


with DAG('user_automation',
         default_args=default_args,
         schedule_interval="@daily",
         catchup=False) as dag:
    with TaskGroup('streaming_tasks', tooltip='Tasks for parallel streaming data') as streaming_tasks:
        for i in range(3):  # Open 3 threads to parallel request api information.
            streaming_task = PythonOperator(
                task_id=f'streaming_task_{i}',
                python_callable=streaming_data
            )

    streaming_task = PythonOperator(
        task_id='streaming_task',
        python_callable=streaming_data
    )

    check_table_exists = PythonOperator(
        task_id='check_table_exists',
        python_callable=check_db_exist
    )

    consume_and_store_data = PythonOperator(
        task_id='consume_and_store_data',
        python_callable=consume_and_store_data
    )



streaming_task >> check_table_exists >> consume_and_store_data