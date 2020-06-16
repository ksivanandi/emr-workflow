from workflow_read_and_write import standard_read_from_db, readmission_classifier_write_to_db
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
import pickle

def create_dataset(df):
    tfidfconverter = TfidfVectorizer(max_features=5000, strip_accents='unicode', decode_error = 'ignore', stop_words = stopwords.words('english'))
    X = tfidfconverter.fit_transform(df['readmission_classifier_tokens'].to_list()).toarray()
    y = df['readmission'].to_numpy()
    
    # We're not using the splitting of the data currently. Since we only want the raw probabilities,
    # I have the classifier fitting to the whole dataset.
    #train_test_split.stratify = True
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 0, stratify = y)

    return X, y

def train_classifier(X, y):
    #Should the class weight be redistributed since there are far less readmissions than non-readmissions?
    #I think with the weights set as is, they put even less emphasis on the readmissions.
    classifier = RandomForestClassifier(n_estimators = 1000, random_state = 0, class_weight = {0:0.8,1:0.2})
    classifier.fit(X, y)

    return classifier

def make_probability_column(classifier, input_features):
    y_hat = classifier.predict_proba(input_features)[:,1]
    return y_hat
    

def train_and_predict():
    df_json_encoded = standard_read_from_db('readmission_classifier_tokens')
    df = pd.read_json(df_json_encoded.decode())
    
    X, y = create_dataset(df)
    classifier = train_classifier(X, y)

    probabilities = make_probability_column(classifier, X)
    df['readmission_classifier_probabilities'] = probabilities

    df_json_encoded = df.to_json().encode()
    classifier_pickle = pickle.dumps(classifier)

    readmission_classifier_write_to_db(df_json_encoded, classifier_pickle)
