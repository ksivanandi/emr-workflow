from spacy.tokens import Doc
from spacy.vocab import Vocab
from pkg_resources import resource_filename
import os
import time

#Prepare for data frame
entity_list = ['index','record_id', 'mass_unit', 'volume_unit', 'time_unit', 'route_type', 'form_unit', 'frequency_indicator', 'measurement_unit', 'measurement', 'duration_pattern', 'clock', 'drug', 'diagnosis', 'admission_date','discharge_date', 'temperature', 'blood_pressure','length_of_stay', 'los_code', 'identified_entities']

#For ALL Entity Values
entity_all_column_title_list=[]
entity_all_column_content_list=[]

for entity_title in entity_list:
    content=[]
    entity_all_column_content_list.append(content)

#dictionary for ALL records
all_result_dict = dict(zip(entity_list, entity_all_column_content_list))

#somehow get the json data from step_1.1, placeholder for now
records ={[{'doc':'',vocab_bytes:''},{'doc':'',vocab_bytes:''},{'doc':'',vocab_bytes:''}]}

for record in records:
    vocab = Vocab().from_bytes(record['vocab_bytes'])
    doc = Doc(vocab).from_bytes(record['doc_bytes']) 
    ents = list(doc.ents)

    #initialize for this new record
    ents_in_a_record = []

    #For each record
    record_entity_column_content_list=[]



