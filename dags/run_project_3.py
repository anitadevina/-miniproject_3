from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models import Connection

from datetime import datetime

from modules.et_q1 import *
from modules.et_q2 import *
from modules.load import *

conn = Connection.get_connection_from_secrets("postgres-server-ftde")


def func_exec_et_top_countries():
    extract_transform_top_countries(conn)


def func_exec_et_total_films_by_category():
    extract_transform_total_films_by_category(conn)


def func_load_top_countries():
    ingest_top_countries()


def func_load_total_films_by_category():
    ingest_total_films_by_category()


with DAG(
    dag_id="run_project_3",
    start_date=datetime(2022, 5, 28),
    schedule_interval="0 * 1 * *",
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="start")

    op_et_top_countries = PythonOperator(
        task_id="extract_transform_top_countries",
        python_callable=func_exec_et_top_countries,
    )

    op_et_total_films_by_category = PythonOperator(
        task_id="extract_transform_total_films_by_category",
        python_callable=func_exec_et_total_films_by_category,
    )

    op_load_top_countries = PythonOperator(
        task_id="load_top_countries",
        python_callable=func_load_top_countries,
    )

    op_load_total_films_by_category = PythonOperator(
        task_id="load_total_films_by_category",
        python_callable=func_load_total_films_by_category,
    )

    end_task = EmptyOperator(task_id="end")

start_task >> op_et_top_countries
start_task >> op_et_total_films_by_category

check_point = EmptyOperator(task_id="check_point_after_extract_transform")

[op_et_top_countries, op_et_total_films_by_category] >> check_point
check_point >> op_load_top_countries >> op_load_total_films_by_category >> end_task