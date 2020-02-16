from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import first_table_from_api
import word2vec_prep_clean_notes
import word2vec_prep_tokenize_notes
import ngram_prep_tokenize_notes
import create_word2vec_model
import entity_recognition
import fe_from_readmission_keywords
import fe_from_infection_keywords
import fe_from_structured_readmit_los
import fe_vitals_ngram_creation
import create_lda_model
import use_ner_model
import combine_dataframes

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

word2vec_clean_notes_operator = PythonOperator(
    task_id = 'word2vec_prep_cleanse_notes',
    python_callable = word2vec_prep_clean_notes.clean_all_notes(),
    dag = dag
    )

word2vec_tokenize_notes_operator = PythonOperator(
    task_id = 'word2vec_prep_tokenize_notes',
    python_callable = word2vec_prep_tokenize_notes.tokenize_all_notes,
    dag = dag
    )

word2vec_operator = PythonOperator(
    task_id = 'make_word2vec_model',
    python_callable = create_word2vec_model.create_word2vec_model,
    dag = dag
    )

create_lda_model_operator = PythonOperator(
    task_id = 'create_lda_model',
    python_callable = create_lda_model.create_lda_model,
    dag = dag
    )

fe_ngram_prep_tokenize_notes_operator = PythonOperator(
    task_id = 'fe_ngram_prep_tokenize_notes',
    python_callable = ngram_prep_tokenize_notes.add_tokens_column,
    dag = dag
    )

fe_vitals_ngram_creation_operator = PythonOperator(
    task_id = 'create_vitals_ngrams',
    python_callable = fe_vitals_ngram_creation.create_vitals_ngrams,
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

structured_features_operator = PythonOperator(
    task_id = 'fe_from_structured_data',
    python_callable = fe_from_structured_readmit_los.create_structured_data_features,
    dag = dag
    )

label_with_ner_operator = PythonOperator(
    task_id = 'label_note_with_ner_model',
    python_callable = use_ner_model.run_ner_on_notes(),
    dag = dag
    )

combine_all_dataframes_operator = PythonOperator(
    task_id = 'combine_data_frames_for_tpot',
    python_callable = combine_dataframes.combine(),
    dag = dag
    )

df_from_api_operator >> word2vec_clean_notes_operator >> word2vec_tokenize_notes_operator >> word2vec_operator >> [entity_recognition >> [fe_ngram_prep_tokenize_notes_operator >> fe_vitals_ngram_creation_operator], [infected_one_hot_operator, structured_features_operator]] >> combine_all_dataframes_operator
