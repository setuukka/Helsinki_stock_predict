import yfinance as yf
import pandas as pd
from datetime import date
from datetime import datetime, timedelta
import numpy as np
#from sklearn.linear_model import LinearRegression
from scipy.stats import linregress, skew, kurtosis

df = pd.read_csv("single_measures_df.csv")
print(df.dtypes)
