# Project
A small project for ETL pipeline and implement some notify functions.


# Functions
1. Send a simple request to api and through ETL pipeline and store to database.
2. Support when task success/failed that can notify user via Discord and Emails.


# What's inside?
1. Apache airflow original image
2. Postgres official image
3. Zookeeper & Kafka images from confluentinc provided

# Usage
1. cd your folder where you clone this project 
2. Open the terminal and type in docker compose up airflow-init
3. wait for it
4. docker compose up -d
5. Go web and type in your url: localhost:8080/home