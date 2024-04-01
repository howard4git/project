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
