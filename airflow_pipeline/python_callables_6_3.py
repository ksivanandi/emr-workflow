from first_table_from_api import get_dataframe_from_apis
from fe_from_structured_readmit_los import create_structured_data_features
from word2vec_prep_clean_notes import clean_all_notes as word2vec_all_clean_notes
from word2vec_prep_tokenize_notes import tokenize_all_notes as word2vec_all_tokenize_notes
from create_word2vec_model import create_word2vec_model as word2vec_all_create_model
from fe_from_infection_keywords import infected_one_hot
from readmission_word2vec_prep_clean_notes import clean_readmission_notes
from readmission_word2vec_prep_tokenize_notes import toeknize_readmission_notes
from create_readmission_word2vec_model import create_word2vec_mode as word2vec_readmission_create_model
from fe_from_readmission_keywords import readmission_one_hot
from ner_prep_clean_notes import clean_ner_notes
from make_all_note_lines_file import create_file
from inference_per_100000 import label_notes
from create_entity_columns import create_entity_columns

get_dataframe_from_apis()
print('1. Done creating dataframe')
create_structured_data_features()
print('2. Done creating structured data features')
word2vec_all_clean_notes()
print('3. Done cleaning notes word2vec all')
word2vec_all_tokenize_notes()
print('4. Done tokenizing notes word2vec all')
word2vec_all_create_model()
print('5. Done creating model word2vec all')
infected_one_hot()
print('6. Done one-hot-encoding infected keywords with word2vec all model')
clean_readmission_notes()
print('7. Done cleaning notes word2vec readmission')
tokenize_readmission_notes()
print('8. Done tokenizing notes word2vec readmission')
word2vec_readmission_create_model()
print('9. Done creating model word2vec readmission')
readmission_one_hot()
print('10. Done one-hot-encoding readmission keywords with word2vec readmission model')
clean_ner_notes()
print('11. Done cleaning notes NER')
create_file()
print('12. Done creating all note lines file for NER processing')
label_notes()
print('13. Done labeling notes with NER Model')
create_entity_columns()
print('14. Done creating entity columns from the NER-labeled notes')

