import pandas as pd
import datetime
from workflow_read_and_write import standard_read_from_db, summary_report_write_to_db, xgb_read_from_db

def make_patient_summary(df):
    summary_df = pd.DataFrame()
    
    # get unique patient ids
    patient_ids = df['patient_id'].unique()
    #iterate through patient ids to create rows for the df
    for pat_id in patient_ids:
        #create filter of rows that match patient id pat_id
        is_patient = df['patient_id'] == pat_id
        # apply filter
        pat_df = df[is_patient]
        # change admittime column to datetime data type
        pat_df['admittime'] = pd.to_datetime(pat_df['admittime'])
        
        # get the number of readmissions
        num_readmissions = pat_df['readmission'].sum()
        
        # get admissions for past year and get a list of all icd_codes
        adm_past_year = 0
        now = datetime.datetime.now()
        year = pd.to_timedelta('365 days 00:00:00')
        past_year = now - year
        #initialize an empty list for the icd codes
        icd_codes = []
        for i, row in pat_df.iterrows():

            icd_codes += row['icd_codes']

            if row['admittime'] >= past_year:
                adm_past_year += 1

        #remove duplicates
        icd_codes = list(dict.fromkeys(icd_codes))
        
        #get the average los for a given patient
        los_avg = pat_df['los'].mean()

        # get most recent age and gender identity 
        # sort the dataframe based on admittime column in ascending order
        pat_df.sort_values(by=['admittime'], inplace=True, ascending=True)
        age = pat_df.iloc[-1]['age']
        gender = pat_df.iloc[-1]['gender']

        #MW: not currently in script for the first dataframe, I have some code snippets for these values though.
        insurance = pat_df.iloc[-1]['insurance']
        dx_description = pat_df.iloc[-1]['diagnosis']

        # create the row as a dictionary
        summary_row = {
                'patient_id': pat_id,
                'readmission_count': num_readmissions,
                '12_month_admission_count': adm_past_year,
                'los_avg': los_avg,
                'icd_codes': icd_codes,
                'age': age,
                'gender': gender,
                'insurance_type': insurance,
                'dx_description': dx_description
                }
        # add the row for a given patient
        summary_df.append(summary_row, ignore_index=True)

    return summary_df


def make_hospital_summary(df, top_terms_dict, readmission_word2vec):
    summary_df = pd.DataFrame()
    row = {}

    row['total_admissions'] = len(df)
    
    #create lists of unique values for icd codes, insurance, and gender
    icd_codes = []
    for i, row in df.iterrows():
        icd_codes += row['icd_codes']
    #deduplicate icd_codes
    icd_codes = list(dict.fromkeys(icd_codes))
    pos_ins_vals = df['insurance'].unique()
    pos_gend_vals = df['gender'].unique()

    row['total_readmissions'] = df['readmission'].sum()
    #filter for other readmission counts
    readmission_df = df[df['readmission']]
    for val in pos_ins_vals:
        is_val = readmission_df['insurance'] == val
        filtered_df = readmission_df[is_val]
        row['Insurance: ' + val + ' readmission_count'] = len(filtered_df)
    for val in pos_gend_vals:
        is_val = readmission_df['gender'] == val
        filtered_df = readmission_df[is_val]
        row['Gender: ' + val + ' readmission_count'] = len(filtered_df)

    #get top 10 icd codes by readmission count:
    readmission_icd_codes = []
    for i, row in readmission_df.iterrows():
        readmission_icd_codes += row['icd_codes']
    # deduplicate the list. reference: https://www.w3schools.com/python/python_howto_remove_duplicates.asp
    readmission_icd_codes = list(dict.fromkeys(readmission_icd_codes))
    #This will keep a count of all the icd codes. The keys will be the codes, the values will be the counts:
    readm_icd_count_dict = {}
    for code in readmission_icd_codes:
        #create filter column to remove rows that don't have a given icd code
        in_codes =[]
        for i, row in df.iterrows():
            in_codes.append(code in row['icd_codes'])
        #Use the filter to remove the rows without a given icd code
        filtered_df = df[in_codes]
        readm_icd_count_dict[code] = len(filtered_df)
    # sort the icd code dictionary based on count
    readm_icd_count_sorted = {k: v for k, v in sorted(readm_icd_count_dict.items(), key=lambda item: item[1])}
    # get the top 10 codes from the sorted list
    top_10_icd_readm = list(readm_icd_count_sorted)[-10:]
    row['top_10_icd_codes_readmission_count'] = top_10_icd_readm


    row['overall_los_avg'] = df['los'].mean()
    #filter for other los averages
    
    # get los average for possible insurance types
    for val in pos_ins_vals:
        is_val = df['insurance'] == val
        filtered_df = df[is_val]
        avg_los = filtered_df['los'].mean()
        row['Insurance: ' + val + ' los_avg'] = avg_los

    # get los average for possible gender values
    for val in pos_gend_vals:
        is_val = df['gender'] == val
        filtered_df = df[is_val]
        avg_los = filtered_df['los'].mean()
        row['Gender: ' + val + ' los_avg'] = avg_los

    # create a dictionary to keep track of the average los for a given icd code
    icd_codes_los_dict = {}
    #initialize empty list that will be used as a filter
    in_codes = []
    # iterate through icd codes
    for code in icd_codes:
        # iterate through dataframe rows to append values to the filter in_codes
        for i, row in df.iterrows():
            # append a boolean value if a given icd code is present for a given row
            in_codes.append(code in row['icd_codes'])
        # apply the filter
        filtered_df = df[in_codes]
        # compute average los
        avg_los = filtered_df['los'].mean()
        # add entry to the dictionary: icd code is the key, average los is the value
        icd_codes_los_dict['ICD Code: ' + code + ' average los'] = avg_los
    # sort the dictionary based on average los values
    icd_los_sorted = {k: v for k, v in sorted(icd_codes_los_dict.items(), key=lambda item: item[1])}
    # get top 10 icd codes from the sorted dictionary
    top_10_icd_los = list(icd_los_sorted)[-10:]
    # make a row entry for the top 10 icd codes from los 
    row['top_10_icd_codes_from_los'] = top_10_icd_los
    # add average los for each icd code to the row
    row.update(icd_codes_los_dict)

    # make row entries for the top 3 terms from each xgboost model
    row['top_3_terms_feat_los'] = top_terms_dict['top_n_feat_los_df'].columns
    row['top_3_terms_neg_feat_los'] = top_terms_dict['top_n_neg_feat_los_df'].columns
    row['top_3_terms_med_los'] = top_terms_dict['top_n_med_los_df'].columns
    row['top_3_terms_neg_med_los'] = top_terms_dict['top_n_neg_med_los_df'].columns
    row['top_3_terms_feat_readmissions'] = top_terms_dict['top_n_feat_readm_df'].columns
    row['top_3_terms_neg_feat_readmissions'] = top_terms_dict['top_n_neg_feat_readm_df'].columns
    row['top_3_terms_med_readmissions'] = top_terms_dict['top_n_med_readm_df'].columns
    row['top_3_terms_neg_med_readmissions'] = top_terms_dict['top_n_neg_med_readm_df'].columns

    #top 10 icd codes by readmissions from word2vec model
    row['readmission_themes'] = readmission_word2vec.most_similar('readmission', topn=10)

    # Add the row to the dataframe. Since there is only one row, may not need a dataframe.
    # It is kept for now for consistency's sake.
    summary_df.append(row)
    return summary_df

def create_report():
    # get the dataframe from the structured data features step
    df_json_encoded = standard_read_from_db('structured_data_features')
    structured_df = pd.read_json(df_json_encoded.decode())
    
    # create patient summary df
    patient_summary_df = make_patient_summary(structured_df)

    # retrieve the top n terms dataframe from each xgboost step
    _, top_n_feat_los_df_json_encoded, _ = xgb_read_from_db('feat_xgb_los')
    top_n_feat_los_df = pd.read_json(top_n_feat_los_df_json_encoded.decode())

    _, top_n_neg_feat_los_df_json_encoded, _ = xgb_read_from_db('neg_feat_xgb_los')
    top_n_neg_feat_los_df = pd.read_json(top_n_neg_feat_los_df_json_encoded.decode())

    _, top_n_med_los_df_json_encoded, _ = xgb_read_from_db('med_xgb_los')
    top_n_med_los_df = pd.read_json(top_n_med_los_df_json_encoded.decode())

    _, top_n_neg_med_los_df_json_encoded, _ = xgb_read_from_db('neg_med_xgb_los')
    top_n_neg_med_los_df = pd.read_json(top_n_neg_med_los_df_json_encoded.decode())

    _, top_n_feat_readm_df_json_encoded, _ = xgb_read_from_db('feat_xgb_readmission')
    top_n_feat_readm_df = pd.read_json(top_n_feat_readm_df_json_encoded.decode())

    _, top_n_neg_feat_readm_df_json_encoded, _ = xgb_read_from_db('neg_feat_xgb_readmission')
    top_n_neg_feat_readm_df = pd.read_json(top_n_neg_feat_readm_df_json_encoded.decode())

    _, top_n_med_readm_df_json_encoded, _ = xgb_read_from_db('med_xgb_readmission')
    top_n_med_readm_df = pd.read_json(top_n_med_readm_df_json_encoded.decode())

    _, top_n_neg_med_readm_df_json_encoded, _ = xgb_read_from_db('neg_med_xgb_readmission')
    top_n_neg_med_readm_df = pd.read_json(top_n_neg_med_readm_df_json_encoded.decode())

    # Create a dictionary of all the top n dataframes.
    # This will be passed into the function that creates the hospital summary. 
    top_n_dict = {
            'top_n_feat_los_df': top_n_feat_los_df,
            'top_n_neg_feat_los_df': top_n_neg_feat_los_df,
            'top_n_med_los_df': top_n_med_los_df,
            'top_n_neg_med_los_df': top_n_neg_med_los_df,
            'top_n_feat_readm_df': top_n_feat_readm_df,
            'top_n_neg_feat_readm_df': top_n_neg_feat_readm_df,
            'top_n_med_readm_df': top_n_med_readm_df,
            'top_n_neg_med_readm_df': top_n_neg_med_readm_df
            }

    # Get the word2vec model for readmissions.
    readmission_word2vec_model_pickle = standard_read_from_db('readmission_word2vec')
    readmission_word2vec_model = pickle.loads(readmission_Word2vec_model_pickle)
    
    # create hospital summary df
    hospital_summary_df = make_hospital_summary(structured_df, top_n_dict, readmission_word2vec_model)

    # serialize patient and hospital summary dataframes
    patient_summary_df_json_encoded = patient_summary_df.to_json().encode()
    hospital_summary_df_json_encoded = hospital_summary_df.to_json().encode()

    # Persist serialized dataframes into the database
    summary_report_write_to_db(patient_summary_df_json_encoded, hospital_summary_df_json_encoded)

