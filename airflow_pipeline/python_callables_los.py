from first_table_from_api import get_dataframe_from_apis
from word2vec_prep_clean_notes import clean_all_notes
from word2vec_prep_tokenize_notes import tokenize_all_notes
from readmission_word2vec_prep_clean_notes import clean_readmission_notes
from readmission_word2vec_prep_tokenize_notes import tokenize_readmission_notes
from create_word2vec_model import create_word2vec_model
from create_readmission_word2vec_model import create_word2vec_model as readmission_create_word2vec_model
from ngram_prep_tokenize_notes import add_tokens_column
from fe_vitals_ngram_creation import create_vitals_ngrams
from fe_from_readmission_keywords import readmission_one_hot
from fe_from_infection_keywords import infected_one_hot
from fe_from_structured_readmit_los import create_structured_data_features 
from combine_dataframes import combine
from run_tpot_los import run_tpot

#get_dataframe_from_apis()
#print("1. Done get_dataframe_from_apis")
create_structured_data_features()
print("2. Done create_structured_data_features")
#clean_all_notes()
#print("3. Done clean_all_notes")
#tokenize_all_notes()
#print("4. Done tokenize_all_notes")
clean_readmission_notes()
print("5. Done clean_readmission_notes")
tokenize_readmission_notes()
print("6. Done tokenize_readmission_notes")
#create_word2vec_model()
#print("7. Done create_word2vec_model")
readmission_create_word2vec_model()
print("8. Done readmission_create_word2vec_model")
#add_tokens_column()
#print("9. Done add_tokens_column")
#create_vitals_ngrams()
#print("10. Done create_vitals_ngrams")
#infected_one_hot()
#print("11. Done infected_one_hot")
readmission_one_hot()
print("12. Done readmission_one_hot")
combine()
print("13. Done combine")
#run_tpot()
#print("14. Done run_tpot")
