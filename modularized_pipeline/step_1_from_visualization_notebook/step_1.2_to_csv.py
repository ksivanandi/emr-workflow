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
records ={'records':[{'doc_bytes':'','vocab_bytes':''},{'doc_bytes':'','vocab_bytes':''},{'doc_bytes':'','vocab_bytes':''}]}

for record in records:
    vocab = Vocab().from_bytes(record['vocab_bytes'])
    doc = Doc(vocab).from_bytes(record['doc_bytes']) 
    ents = list(doc.ents)

    #initialize for this new record
    ents_in_a_record = ents

    #For each record
    record_entity_column_content_list=[]

    for entity_title in entity_list:
        content=[]
        record_entity_column_content_list.append(content)
    record_result_dict = dict(zip(entity_list, record_entity_column_content_list))

    ents_in_a_record.append(entity.orth_)
    record_result_dict[entity.label_].append(entity.orth_)

    #end of a record OR end of ents
    record_result_dict['identified_entities'].append(ents_in_a_record)
    
    #end of a record
    admit_dt = record_result_dict['admission_date']
    discharge_dt = record_result_dict['discharge_date']

    t1 = pd.to_datetime(admit_dt, errors = 'coerce')
    t2 = pd.to_datetime(discharge_dt, errors = 'coerce')

    dt_code = 0
    t = np.nan

    if (admit_dt == ''):
        dt_code = dt_code + 8
    elif (discharge_dt == '' ):
        dt_code = dt_code + 4
    elif (pd.isnull(t1)):
        dt_code = dt_code + 2
    elif (pd.isnull(t2)):
        dt_code = dt_code + 1
    else:
        try:
            #t = abs((t2 - t1).days[0])
            t0=t2-t1
            #t = t0.days
            t = abs(t0.days[0])
        except:
            print("Length of Stay Except", t2, t1 )
        pass

    try:
        record_result_dict["length_of_stay"].append(t)
        record_result_dict["index"].append(record_index)
        record_result_dict["los_code"].append(dt_code)
    except:
        print("Length of Stay Except", t )
        pass

    for x in record_result_dict:
        if (record_result_dict[x]==[]):
            record_result_dict[x].append(np.nan)
        all_result_dict[x].append(record_result_dict[x])

df=pd.DataFrame(all_result_dict)
json_dataframe = df.to_json()
