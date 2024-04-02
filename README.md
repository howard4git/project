# project


Ref:
https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

先 docker compose up airflow-init
再 docker compose up 

## Zookeeper settings
docker run -d \
    --name zookeeper \
    --network trinity \
    -e ZOO_MY_ID=1 \
    -e ZOO_SERVERS=server.1=zookeeper:2888:3888 \
    -e ZOO_TICK_TIME=2000 \
    -e ZOO_INIT_LIMIT=5 \
    -e ZOO_SYNC_LIMIT=2 \
    -p 2181:2181 \
    -p 2888:2888 \
    -p 3888:3888 \
    zookeeper:latest 

----------------------------------
## create a network
docker network create {name}

## remove a network
docker network rm trinity
----------------------------------


## Kafka settings
docker run -d \
    --name kafka \
    --network trinity \
    -e KAFKA_LISTENERS=PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092 \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092,PLAINTEXT_HOST://localhost:29092 \
    -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT \
    -e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT \
    -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
    -p 9092:9092 \
    -p 29092:29092 \
    confluentinc/cp-kafka:latest
----------------------------------

##SQL

docker run --name postgres -e POSTGRES_PASSWORD=123 -p 5432:5432 --network trinity -d postgres:14.0

## docker 掛載卷 to presist data
docker run --name postgres -e POSTGRES_PASSWORD=123 -p 5432:5432 --network trinity -v postgres-data:/var/lib/postgresql/data -d postgres:14.0

bash in kafka container 
config path : /opt/$imaage_name(bitnami)/kafka/config
# set consumer groupid
consumer.properties
/opt/bitnami/kafka/bin$ kafka-broker-api-versions.sh --bootstrap-server localhost:9092
##
可以用 whereis 確定檔案路徑在哪

## Trouble shooting:

ERROR Exiting Kafka due to fatal exception during startup. (kafka.Kafka$) kafka.common.InconsistentClusterIdException: The Cluster ID 77PZKMMvRVuedQzKixTIQA doesn't match stored clusterId Some() in meta.properties. The broker is trying to join the wrong cluster. Configured zookeeper.connect may be wrong.

Solution for Mac on homebrew kafka installation:

open /opt/homebrew/var/lib/kafka-logs/meta.properties and replace cluster.id by YOUR cluster ID in the message, as above.
delete folder of logs rm -r /opt/homebrew/var/run/zookeeper/data/
reset your zookeeper and kafka.
Share
Improve this answer
Follow

##
一個DAG 底下有 123456個任務 (1:n)
DAG建議和python檔名一樣
e.g.
with DAG(
    dag_id = 'first_dag',
    start_date = datetime(2023, 9, 22),
    schedule_interval='@daily'
) as dag:
    task1 = BashOperator(
        task_id='task1',
        bash_command="echo start!!"
    )

    task2 = PythonOperator(
        task_id='task2',
        python_callable= func name
    )

task1 >> task2
## airflow cheat-sheet

## TO STUDY
https://github.com/lukeburciu/hpviz/issues/71
https://stackoverflow.com/questions/59592518/kafka-broker-doesnt-find-cluster-id-and-creates-new-one-after-docker-restart