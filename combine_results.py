import pandas as pd



predicted_df = pd.read_csv("predicted_results.csv")
#Lower case all column names
predicted_df.columns = [column.lower() for column in predicted_df.columns]
#Drop if Unnamed anything excists
predicted_df = predicted_df.loc[:, ~predicted_df.columns.str.contains('unnamed', case=False)]
#print(predicted_df)

#predicted_df = predicted_df[['date','company','Regression Prediction','Random Forest Prediction','XGBoost Prediction']]
actual_df = pd.read_csv("single_measures_df.csv", index_col = 0)
actual_df.reset_index(inplace = True)

#Lower case all column names
actual_df.columns = [column.lower() for column in actual_df.columns]

#Drop if Unnamed anything excists
actual_df = actual_df.loc[:, ~actual_df.columns.str.contains('unnamed', case=False)]
#Take only first ten digits as date
actual_df['date'] = actual_df['date'].apply(lambda x : x[:10])


print(len(predicted_df))

joined_df = pd.merge(actual_df, predicted_df, on= ['date','company'], how = 'inner')
#print(joined_df)