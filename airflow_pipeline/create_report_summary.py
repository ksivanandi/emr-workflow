import pandas as pd
import datetime
from workflow_read_and_write import standard_read_from_db

def make_patient_summary(df):
    summary_df = pd.DataFrame()

    patient_ids = df['patient_id'].unique()
    for pat_id in patient_ids:
        is_patient = df['patient_id'] == pat_id
        pat_df = df[is_patient]
        pat_df['admittime'] = pd.to_datetime(pat_df['admittime'])
        num_readmissions = pat_df['readmission'].sum()
        
        adm_past_year = 0
        now = datetime.datetime.now()
        year = pd.to_timedelta('365 days 00:00:00')
        past_year = now - year
        icd_codes = []
        for i, row in pat_df.iterrows():
            icd_codes += row[icd_codes]

            if row['admittime'].to_datetime() >= past_year:
                adm_past_year += 1

        #remove duplicates
        icd_codes = list(dict.fromkeys(icd_codes))
        
        los_avg = pat_df['los'].mean()
        last_ind = len(pat_df) - 1

        age = pat_df.iloc[-1]['age']
        gender = pat_df.iloc[-1]['gender']

        #MW: not currently in script for the first dataframe, I have some code snippets for these values though.
        insurance = pat_df.iloc[-1]['insurance']
        dx_description = pat_df.iloc[-1]['diagnosis']

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

        summary_df.append(summary_row)

    return summary_df


def create_report():
    df_json_encoded = standard_read_from_db('structured_data_features')
    structured_df = pd.read_json(df_json_encoded.decode())
    
    patient_summary_df = make_patient_summary(structured_df)

    #have to figure out the parameters to pass in for hospital_summary_df, likely the top_n_dfs from xgb steps

