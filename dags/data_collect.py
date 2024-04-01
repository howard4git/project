from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# 定義一個 Python 函數，這個函數將會在 DAG 中執行
def my_python_function():
    print("Hello, Airflow!")

# 定義 DAG 的參數
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022, 1, 1),
    'retries': 1
}

# 定義一個 DAG 對象
dag = DAG(
    'my_simple_dag',
    default_args=default_args,
    description='A simple DAG',
    schedule_interval='@daily',
    catchup=False
)

# 定義一個 PythonOperator，用於執行上面定義的 my_python_function
run_this = PythonOperator(
    task_id='print_hello',
    python_callable=my_python_function,
    dag=dag
)

# 將運算子與 DAG 相關聯
run_this
