from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pre_processing_Create_Tokens
import pre_processing_Create_Word2Vec_model
import feature_engineering_Sequence_Clinical_Note
import feature_engineering_Topic_Modeling
import feature_engineering_Vitals_Related_Added
import tpot_prep_One_Hot_Encoding_Diagnoses
import tpot_prep_One_Hot_Encoding_Medications

from datetime import datetime, timedelta

default_args = {
    'owner': 'Morgan EMR Pipeline',
    'start_date': datetime(2020,1,24)
}

dag = DAG('emr-initial-dag', default_args=default_args)

tokenize_operator = PythonOperator(
    task_id = 'pre_processing_create_tokens',
    python_callable = pre_processing_Create_Tokens.teokenize_data,
    dag = dag
    )

word_embedding_operator = PythonOperator(
    task_id = 'pre_processing_create_word2vec_model',
    python_callable = pre_processing_Create_Word2Vec_model.create_and_save_word2vec,
    dag = dag
    )

admit_discharge_features_operator = PythonOperator(
    task_id = 'feature_engineering_admit_discharge',
    python_callable = feature_engineering_Sequence_Clinical_Note.add_admit_discharge_columns,
    dag = dag
    )

topic_modeling_operator = PythonOperator(
    task_id = 'feature_engineering_topic_modeling',
    python_callable = feature_engineering_Topic_Modeling.run_topic_modeling,
    dag = dag
    )

vitals_ngrams_features_operator = PythonOperator(
    task_id = 'feature_engineering_vitals_ngrams',
    python_callable = feature_engineering_Vitals_Related_Added.add_vitals_ngrams_columns,
    dag = dag
    )

diagnoses_one_hot_operator = PythonOperator(
    task_id = 'tpot_prep_diagnoses_one_hot',
    python_callable = tpot_prep_One_Hot_Encoding_Diagnoses.diagnoses_one_hot_encoding,
    dag = dag
    )

medications_one_hot_operator = PythonOperator(
    task_id = 'tpot_prep_medications_one_hot',
    python_callable = tpot_prep_One_Hot_Encoding_Medications.medications_one_hot_encoding,
    dag = dag
    )

tokenize_operator >> [word_embedding_operator, admit_discharge_features_operator, topic_modeling_operator] >> vitals_ngrams_features_operator >> diagnoses_one_hot_operator >> medications_one_hot_operator
