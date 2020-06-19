from sklearn.preprocessing import MultiLabelBinarizer
import xgboost as xgb
import pandas as pd
import pickle
from workflow_read_and_write import standard_read_from_db, xgb_write_to_db

def make_one_hot(df):
    mlb = MultiLabelBinarizer()
    feature_entities = df['feature_entities']
    feat_one_hot = (pd.DataFrame(mlb.fit_transform(medication_entities), columns=mlb.classes_,index=df.index))

    return feat_one_hot

def train_xgb_model(df):
    feat_one_hot = make_one_hot(df)
    labels = pd.DataFrame(df['readmission'])
    data = xgb.DMatrix(feat_one_hot, label=labels)

    #tuning opportunity (grid search)
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
    feat_one_hot = make_one_hot(df)
    data = xgb.DMatrix(feat_one_hot)
    predictions = bst.predict(data)
    df['xgb_feat_ent_pred'] = predictions

    return df

def make_predictions():
    df_json_encoded = standard_read_from_db('entity_columns')
    df = pd.read_json(df_json_encoded.decode())
    
    bst = train_xgb_model(df)
    
    df = add_predictions_column(df, bst)

    df_json_encoded = df.to_json().encode()
    bst_pickle = pickle.dumps(bst)

    xgb_write_to_db('feat_xgb', df_json_encoded, bst_pickle)
