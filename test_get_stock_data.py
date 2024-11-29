#Test file. Does not overwrite csv

import yfinance as yf
import pandas as pd
from datetime import date
from datetime import datetime, timedelta
import numpy as np
#from sklearn.linear_model import LinearRegression
from scipy.stats import linregress, skew, kurtosis
import time
import json
import warnings


warnings.filterwarnings("ignore", category=RuntimeWarning)


pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)

#Reading stock list from JSON
with open("stocklist.json", "r") as file:
    stocklist = json.load(file)

#for testing
stocklist2 = ["QTCOM.HE","REMEDY.HE","WRT1V.HE.HE"]
stocklist3 = ["WRT1V.HE.HE"]

def generate_complete_datetime_range(start, end, freq='min'):
    """Generates a complete datetime range from start to end with the given frequency."""
    return pd.date_range(start=start, end=end, freq=freq)

def reindex_with_complete_range(df, all_minutes):
    """Reindexes the DataFrame with a complete datetime range, filling missing rows with NaN."""
    return df.reindex(all_minutes)

def forward_fill_missing_values(df):
    """Fills missing values in the DataFrame using forward fill."""
    #return df.fillna(method='ffill')
    return df.ffill()

def ensure_minute_intervals(df, start_time, end_time):
    """
    Main function to ensure DataFrame has a row for every minute between start_time and end_time,
    filling missing rows with previous values.
    """


    all_minutes = generate_complete_datetime_range(start_time, end_time)
    df = reindex_with_complete_range(df, all_minutes)

    count_of_original_values = (len(df) - df['Open'].isna().sum())

    df = forward_fill_missing_values(df)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Datetime'}, inplace=True)
    return df, count_of_original_values

def get_stock_data(stock, start, end):
    return stock.history(start = start, end = end, interval = "1m").reset_index()

def map_percentage_change(stock_data):
    #Calculating percentage change
    stock_data['percentage_change'] = stock_data['Close'].pct_change() * 100
    return stock_data

def set_binary_for_percentage_change(stock_data):
    stock_data['direction'] = stock_data['percentage_change'].apply(lambda x : 1 if x > 0 else 0)
    return stock_data


def get_single_measures_from_data(stock_data, stock):
    data = stock_data['Close']    
    x = np.arange(len(data))
    slope, intercept, r_value, p_value, std_error = linregress(x, data)
    stdev = np.std(data, ddof = 1)
    skewness = skew(data)
    kurt = kurtosis(data)
    up_percentage = sum(stock_data['direction']) / len(data)
    down_percentage = (len(data) - sum(stock_data['direction'])) / len(data)
    return {
        'company' : stock,
        'slope': slope,
        'r_squared': r_value**2,
        'std_error': std_error,
        'stdev': stdev,
        #'skewness': skewness,
        #'kurtosis': kurt,
        'up_percentage' : up_percentage,
        'down_percentage' : down_percentage
    }
#Funktion to add a single measure to dictionary
def add_single_measure(single_measures, measure, value):
    single_measures[measure] = value


def get_target_value(stock_data):
    return stock_data.iloc[-1]['Close'], (stock_data.iloc[-1]['Close'] / stock_data.iloc[0]['Open']) - 1


def wait(length = 0.5):
    #print(f"Waiting for {length} seconds")
    time.sleep(length)

def main():
    today = datetime.now()
    today = today.date() 
    single_measures_list = []

    #reading the csv to get latest date:
    try:
        data = pd.read_csv("single_measures_df.csv")
        print("Data read!") #debug
        startdate = data['date'].max()[:10]
        #print(f"Startdate is {startdate}")
        startdate = datetime.strptime(startdate, '%Y-%m-%d').date()
        #print(startdate, type(startdate))
        #Creating backup file from yesterdays data
        backup_filename = f"single_measures_{startdate}.csv"
        data.to_csv(backup_filename)
        #print(startdate) #DEBUG
    except FileNotFoundError:
        print(f"File not found")
        #return None
    except Exception as e:
        print(f"An error occurred: {e}")
        #return None


    while startdate <= today-timedelta(days=1):
        #print("Starting days loop with startdate:" ,startdate, "and days to deduct", days_to_deduct)

        #Check if weekday is saturday or sunday, continue if True:
        if startdate.weekday() in (5,6):
            print(f"{startdate.strftime('%Y-%m-%d')} is a weekend (Saturday or Sunday).")
            startdate = startdate + timedelta(days=1)
            continue
        #single_measures_df['date'].dt.day_name()

        for company in stocklist2:
            try:
                stock = yf.Ticker(company)
                info = yf.Ticker(company).info
                #for key, value in info.items():
                    #print(key, value)
                if 'longName' in info:
                    company_name = info['longName']
                else:
                    company_name = company
                print(f"{datetime.now()} - {company} on {startdate}")
            except:
                print(f"Error in getting stock info")
                continue

            # Set start and end times

            start_time = f"{startdate} 10:00:00+02:00"
            end_time = f"{startdate} 10:59:00+02:00"

            try:
                stock_data = get_stock_data(stock, startdate, startdate + timedelta(days = 1))
                #print(stock, "shape stock data", stock_data.shape)
                if stock_data.shape[0] == 0:
                    continue
            except:
                continue
            #print(stock_data) #DEBUG

            #Drop unnecessary columns
            stock_data = stock_data.drop(columns=['Dividends','Stock Splits'])
            stock_data.set_index('Datetime', inplace=True)  # Set as index
            #print(stock_data) #DEBUG

            #take the Close value of last row as dependent variably y


            end_day_target_value, end_day_target_percentage = get_target_value(stock_data)
            #print(target_value) #DEBUG


            # Ensure there is a row for each minute, with missing values forward-filled. cuts the df to first hour
            stock_data, count_of_original_values = ensure_minute_intervals(stock_data, start_time, end_time)
            stock_data = map_percentage_change(stock_data)
            stock_data = set_binary_for_percentage_change(stock_data)

            buy_price, irrelevant = get_target_value(stock_data)
            single_measures = get_single_measures_from_data(stock_data, company_name)
            #Add target to single measures
            add_single_measure(single_measures, 'end_day_target_percentage', end_day_target_percentage)
            add_single_measure(single_measures, 'end_day_target_value', end_day_target_value)
            add_single_measure(single_measures, 'count_of_original_values', count_of_original_values)

            add_single_measure(single_measures, 'buy_price', buy_price)
            #Only send 10 first digits to function. That includes YYYY-MM-DD
            add_single_measure(single_measures, 'date', str(startdate)[:10])
            add_single_measure(single_measures, 'end_day_target_percentage', end_day_target_percentage)
            add_single_measure(single_measures, 'ticker',company)

            single_measures_list.append(single_measures)
            wait(1)
        startdate = startdate + timedelta(days=1)
    #wait(3)
    single_measures_df = pd.DataFrame(single_measures_list)
    print(single_measures_df)
    #make the the first
    cols = ['date'] + [col for col in single_measures_df.columns if col != 'date']

    single_measures_df = single_measures_df[cols]
    single_measures_df['date'] = pd.to_datetime(single_measures_df['date'])
    single_measures_df['weekday'] = single_measures_df['date'].dt.day_name()
    #print(single_measures_df)
    #print(single_measures_df)

    joined_df = pd.concat([data, single_measures_df], ignore_index = True)
    #print(data.head(10))
    print(joined_df.tail(10))
    print(f"Old single measures {data.shape}, new data {single_measures_df.shape}, joined data {joined_df.shape}") #DEBUG
    #Removing duplicates and Na values
    old_len = single_measures_df.shape[0]
    single_measures_df = single_measures_df.dropna().drop_duplicates(subset=['date','company'], keep = 'first').reset_index(drop=True)
    print(f"Removed {old_len - single_measures_df.shape[0]} duplicates")
    #Save the df to csv 
    #joined_df.to_csv("single_measures_df.csv", index = False)

main()