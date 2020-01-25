from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pre_processing_Create_Tokens
import pre_processing_Create_Word2Vec_model

dag = DAG('emr-initial-dag')


