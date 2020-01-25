from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pre_processing_Create_Tokens import tokenize_data 
from pre_processing_Create_Word2Vec_model import create_and_save_word2vec
from datetime import datetime, timedelta

default_args = {
    'owner': 'Morgan EMR Pipeline',
    'start_date': datetime(2020,1,24)
}

dag = DAG('emr-initial-dag', default_args=default_args)

tokenize_operator = PythonOperator(
    task_id = 'create_tokens',
    python_callable = tokenize_data,
    dag = dag
    )

word_embedding_operator = PythonOperator(
    task_id = 'create_word2vec_model',
    python_callable = create_and_save_word2vec,
    dag = dag
    )

tokenize_operator >> word_embedding_operator
