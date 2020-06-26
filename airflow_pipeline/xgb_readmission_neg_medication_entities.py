from sklearn.preprocessing import MultiLabelBinarizer
import xgboost as xgb
import pandas as pd
import pickle
from workflow_read_and_write import standard_read_from_db, xgb_write_to_db

def make_one_hot(df):
    mlb = MultiLabelBinarizer()
    medication_entities = df['neg_medication_entities']
    med_one_hot = (pd.DataFrame(mlb.fit_transform(medication_entities), columns=mlb.classes_,index=df.index))

    return med_one_hot

def train_xgb_model(df):
    med_one_hot = make_one_hot(df)
    labels = pd.DataFrame(df['readmission'])
    data = xgb.DMatrix(med_one_hot, label=labels)

    parameters = {
            'booster': 'gbtree', 
            'tree_method':'gpu_hist', 
            'predictor':'gpu_predictor', 
            'subsample':0.5, 
            'sampling_method': 'uniform', 
            'objective':'binary:logistic'
            }

    bst = xgb.train(parameters, data)
    
    return bst
    
def add_predictions_column(df, bst):
    med_one_hot = make_one_hot(df)
    data = xgb.DMatrix(med_one_hot)
    predictions = bst.predict(data)
    df['xgb_med_ent_pred'] = predictions

    return df

def make_top_n_features(bst, one_hot, n):
    scores = bst.get_score(importance_type='gain')
    #https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    scores_sorted = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1])}
    top_n_features = list(scores_sorted)[-n:]

    top_n_df = pd.DataFrame()
    for feature in top_n_features:
        top_n_df[feature] = one_hot[feature]

    return top_n_df

def make_predictions():
    df_json_encoded = standard_read_from_db('entity_columns')
    df = pd.read_json(df_json_encoded.decode())
    
    bst = train_xgb_model(df)
    
    df = add_predictions_column(df, bst)

    top_n_df = make_top_n_features(bst, feat_one_hot, 5)

    df_json_encoded = df.to_json().encode()
    top_n_df_json_encoded = df.to_json().encode()
    bst_pickle = pickle.dumps(bst)

    xgb_write_to_db('neg_med_xgb_readmission', df_json_encoded, top_n_df_json_encoded, bst_pickle)
