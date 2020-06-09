from workflow_read_and_write import standard_read_from_db, standard_write_to_db
import pandas as pd

def some_function_that_does_some_modification_to_a_dataframe(df):
    # do something to the dataframe
    new_df = df
    ...
    ...
    return new_df

def the_callable_that_will_be_used_as_a_task():
    df_json_encoded = standard_read_from_db('the name of the collection used to save the output of the previous step')
    df = pd.read_json(df_json_encoded.decode())

    new_df = some_function_that_does_some_modification_to_a_dataframe(df)

    new_df_json_encoded = new_df.to_json().encode()
    standard_write_to_db('the name of the collection used to save the output of this step')
