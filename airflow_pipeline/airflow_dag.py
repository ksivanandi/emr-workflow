from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pre_processing_Create_Word2Vec_model
import feature_engineering_Sequence_Clinical_Note
import feature_engineering_Topic_Modeling
import feature_engineering_Vitals_Related_Added
import tpot_prep_One_Hot_Encoding_Diagnoses
import tpot_prep_One_Hot_Encoding_Medications

import first_table_from_api
import cleanse_notes
import tokenize_notes
import create_word2vec_model
import entity_recognition
import fe_from_readmission_keywords
import fe_from_infection_keywords

from datetime import datetime, timedelta

default_args = {
    'owner': 'Morgan EMR Pipeline',
    'start_date': datetime(2020,1,24)
}

dag = DAG('emr-initial-dag', default_args=default_args)

df_from_api_operator = PythonOperator(
    task_id = 'standardize_data_format_from_apis',
    python_callable = first_table_from_api.get_dataframe_from_apis,
    dag = dag
    )

clean_notes_operator = PythonOperator(
    task_id = 'cleanse_notes',
    python_callable = cleanse_notes.clean_all_notes(),
    dag = dag
    )

tokenize_notes_operator = PythonOperator(
    task_id = 'tokenize_notes',
    python_callable = tokenize_notes.tokenize_all_notes,
    dag = dag
    )

word2vec_operator = PythonOperator(
    task_id = 'make_word2vec_model',
    python_callable = create_word2vec_model.create_word2vec_model,
    dag = dag
    )

entity_recognition_operator = PythonOperator(
    task_id = 'entity_recognition',
    python_callable = entity_recognition.make_ner,
    dag = dag
    )

readmission_one_hot_operator = PythonOperator(
    task_id = 'fe_readmit_one_hot',
    python_callable = fe_from_readmission_keywords.readmission_one_hot,
    dag = dag
    )

infected_one_hot_operator = PythonOperator(
    task_id = 'fe_infected_one_hot',
    python_callable = fe_from_infection_keywords.infected_one_hot,
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

df_from_api_operator >> clean_notes_operator >> tokenize_notes_operator >> [word_embedding_operator, admit_discharge_features_operator, topic_modeling_operator] >> vitals_ngrams_features_operator >> diagnoses_one_hot_operator >> medications_one_hot_operator
