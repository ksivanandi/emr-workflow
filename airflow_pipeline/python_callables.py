from first_table_from_api import get_dataframe_from_apis
from word2vec_prep_clean_notes import clean_all_notes
from word2vec_prep_tokenize_notes import tokenize_all_notes
from create_word2vec_model import create_word2vec_model
from ngram_prep_tokenize_notes import add_tokens_column
from fe_vitals_ngram_creation import create_vitals_ngrams
from fe_from_readmission_keywords import readmission_one_hot
from fe_from_infection_keywords import infected_one_hot
from fe_from_structured_readmit_los import create_structured_data_features 
from combine_dataframes import combine
from run_tpot_los import run_tpot
from run_tpot_readmission import run_tpot as run_tpot1

get_dataframe_from_apis()
print("1. Done get_dataframe_from_apis")
clean_all_notes()
print("2. Done clean_all_notes")
tokenize_all_notes()
print("3. Done tokenize_all_notes")
create_word2vec_model()
print("4. Done create_word2vec_model")
add_tokens_column()
print("5. Done add_tokens_column")
create_vitals_ngrams()
print("6. Done create_vitals_ngrams")
readmission_one_hot()
print("7. Done readmission_one_hot")
infected_one_hot()
print("8. Done infected_one_hot")
create_structured_data_features()
print("9. Done create_structured_data_features")
combine()
print("10. Done combine")
run_tpot()
print("11. Done run_tpot")
run_tpot1()
print("12. Done run_tpot1")
