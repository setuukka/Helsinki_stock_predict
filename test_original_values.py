#how does the dataframe look like, when original values is considered


import pandas as pd

df = pd.read_csv("single_measures_df.csv")
#print(df[df['count_of_original_values'] > 0])
#print(df['count_of_original_values'].value_counts())

df2 = pd.DataFrame(df['count_of_original_values'].value_counts().reset_index().sort_values(by='count_of_original_values'))
print(df2)