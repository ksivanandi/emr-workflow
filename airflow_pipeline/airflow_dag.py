from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pre_processing_Create_Tokens import tokenize_data 
from pre_processing_Create_Word2Vec_model import create_and_save_word2vec
from feature_engineering_Sequence_Clinical_Note import add_admit_discharge_columns
from feature_engineering_Topic_Modeling import run_topic_modeling
from feature_engineering_Vitals_Related_Added import add_vitals_ngrams_columns
from datetime import datetime, timedelta

default_args = {
    'owner': 'Morgan EMR Pipeline',
    'start_date': datetime(2020,1,24)
}

dag = DAG('emr-initial-dag', default_args=default_args)

tokenize_operator = PythonOperator(
    task_id = 'pre_processing_create_tokens',
    python_callable = tokenize_data,
    dag = dag
    )

word_embedding_operator = PythonOperator(
    task_id = 'pre_processing_create_word2vec_model',
    python_callable = create_and_save_word2vec,
    dag = dag
    )

admit_discharge_features_operator = PythonOperator(
    task_id = 'feature_engineering_admit_discharge',
    python_callable = add_admit_discharge_columns,
    dag = dag
    )

topic_modeling_operator = PythonOperator(
    task_id = 'feature_engineering_topic_modeling',
    python_callable = run_topic_modeling,
    dag = dag
    )

vitals_ngrams_features_operator = PythonOperator(
    task_id = 'feature_engineering_vitals_ngrams',
    python_callable = add_vitals_ngrams_columns,
    dag = dag
    )

tokenize_operator >> [word_embedding_operator, admit_discharge_features_operator, topic_modeling_operator] >> vitals_ngrams_features_operator
