import yfinance as yf
import pandas as pd
from datetime import date
from datetime import datetime, timedelta
import numpy as np
#from sklearn.linear_model import LinearRegression
from scipy.stats import linregress, skew, kurtosis
import time


pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)

stocklist = ["AFAGR.HE","AKTIA.HE","ALMA.HE","ANORA.HE","APETIT.HE","TALLINK.HE","ASPO.HE",
"ACG1V.HE","ATRAV.HE","BIOBV.HE","BITTI.HE","BOREO.HE","CAPMAN.HE","CGCBV.HE","CAV1V.HE",
"CTY1S.HE","CTH1V.HE","CONSTI.HE","DIGIA.HE","DIGIGR.HE","DOV1V.HE","EEZY.HE","ELEAV.HE",
"ELISA.HE","ENENTO.HE","ESENSE.HE","EQV1V.HE","ETTE.HE","EXL1V.HE","FIA1S.HE","FSKRS.HE",
"FORTUM.HE","GLA1V.HE","GOFORE.HE","HARVIA.HE","HKSAV.HE","HONBS.HE","HUH1V.HE","ILKKA2.HE",
"ICP1V.HE","IFA1V.HE","INVEST.HE","KAMUX.HE","KEMIRA.HE","KSLAV.HE","KESKOB.HE",
"KELAS.HE","KOJAMO.HE","KNEBV.HE","KCR.HE","KREATE.HE","LAT1V.HE","MEKKO.HE",
"MARAS.HE","METSO.HE","METSB.HE","MUSTI.HE","NESTE.HE","NOHO.HE",
"NOKIA.HE","TYRES.HE","NDA-FI.HE","NLG1V.HE","OLVAS.HE","OMASP.HE","OPTOMED.HE",
"OKDBV.HE","ORNBV.HE","ORTHEX.HE","OUT1V.HE","OVARO.HE","PNA1V.HE","PIHLIS.HE",
"PON1V.HE","PUMU.HE","PURMO.HE","PUUILO.HE","QPR1V.HE","QTCOM.HE","RAIVV.HE","RAP1V.HE",
"RAUTE.HE","REKA.HE","RELAIS.HE","REMEDY.HE","REG1V.HE","ROBIT.HE","ROVIO.HE","SAGCV.HE",
"SAMPO.HE","SANOMA.HE","SCANFL.HE","SIILI.HE","SITOWS.HE","SOLTEQ.HE","SOSI1.HE","SRV1V.HE",
"SSABBH.HE","SSH1V.HE","STOCKA.HE","STERV.HE","SUY1V.HE","TAALA.HE",
"TNOM.HE","TEM1V.HE","TLT1V.HE","TELIA1.HE","TTALO.HE","TIETO.HE","TOKMAN.HE","TRH1V.HE",
"TULAV.HE","UNITED.HE","UPM.HE","UPONOR.HE","VAIAS.HE","VALMT.HE","VERK.HE",
"VIK1V.HE","WETTERI.HE","WITH.HE","WUF1V.HE","WRT1V.HE","YIT.HE","ALBBV.HE",]

#for testing
stocklist2 = ["AFAGR.HE","SANOMA.HE","TTALO.HE"]
stocklist3 = ["KESKOB.HE"]

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
    df = forward_fill_missing_values(df)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Datetime'}, inplace=True)
    return df

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
    print(f"Waiting for {length} seconds")
    time.sleep(length)

def main():
    today = datetime.now()
    today = today.date() 
    print(today)
    single_measures_list = []

    #Error counter counts if first three stocks come out as zero, program terminates, as the day is holiday, saturday or sunday
    errorcounter = 0


    #reading the csv to get latest date:
    try:
        #data = pd.read_csv("single_measures_df.csv")
        startdate = today
        #Creating backup file from yesterdays data
        #backup_filename = f"single_measures_{startdate}.csv"
        #data.to_csv(backup_filename)
        #print(startdate) #DEBUG
    except FileNotFoundError:
        print(f"File not found")
        #return None
    except Exception as e:
        print(f"An error occurred: {e}")
        #return None



    #Check if weekday is saturday or sunday, continue if True:
    if startdate.weekday() in (5,6):
        print(f"{startdate.strftime('%Y-%m-%d')} is a weekend (Saturday or Sunday).")
        return None

    for company in stocklist:
        try:
            stock = yf.Ticker(company)
            info = yf.Ticker(company).info
            #for key, value in info.items():
                #print(key, value)
            if 'longName' in info:
                company_name = info['longName']
            else:
                company_name = company
            print(f"{company} - {startdate}")
        except:
            print(f"Error in getting stock info")
            continue

        # Set start and end times

        start_time = f"{startdate} 10:00:00+02:00"
        end_time = f"{startdate} 10:59:00+02:00"

        try:
            print(f"Trying to get stock data for {company_name} on {startdate}")
            #stock_data = get_stock_data(stock, (startdate - timedelta(days = 2)), startdate + timedelta(days = 1))
            stock_data = get_stock_data(stock, startdate, startdate+timedelta(days=1))

            #print(stock, "shape stock data", stock_data.shape)
            if stock_data.shape[0] == 0:
                print(f"Stock data for {company_name} is zero")
                errorcounter += 1
                if errorcounter == 3:
                    print("Terminating due to errorcounter")
                    return
                continue
        except:
            continue
        #print(stock_data) #DEBUG

        #Drop unnecessary columns
        stock_data = stock_data.drop(columns=['Dividends','Stock Splits'])
        stock_data.set_index('Datetime', inplace=True)  # Set as index
        #print(stock_data) #DEBUG

        #take the Close value of last row as dependent variably y
        #end_day_target_value, end_day_target_percentage = get_target_value(stock_data)
        #print(target_value) #DEBUG


        # Ensure there is a row for each minute, with missing values forward-filled. cuts the df to first hour
        stock_data = ensure_minute_intervals(stock_data, start_time, end_time)
        stock_data = map_percentage_change(stock_data)
        stock_data = set_binary_for_percentage_change(stock_data)

        #buy_price, irrelevant = get_target_value(stock_data)
        single_measures = get_single_measures_from_data(stock_data, company_name)
        #Add target to single measures
        #add_single_measure(single_measures, 'end_day_target_percentage', end_day_target_percentage)
        #add_single_measure(single_measures, 'end_day_target_value', end_day_target_value)

        #add_single_measure(single_measures, 'buy_price', buy_price)
        add_single_measure(single_measures, 'date', today)
        #add_single_measure(single_measures, 'end_day_target_percentage', end_day_target_percentage)
        add_single_measure(single_measures, 'ticker',company)

        #single_measures['end_day_target_percentage'] = end_day_target_percentage
        #single_measures['end_day_target_value'] = end_day_target_value
        #single_measures['buy_price'] = buy_price
        #single_measures['date'] = date
        single_measures_list.append(single_measures)
        wait(1)

    single_measures_df = pd.DataFrame(single_measures_list)
    #make the the first
    cols = ['date'] + [col for col in single_measures_df.columns if col != 'date']
    single_measures_df = single_measures_df[cols]
    single_measures_df['date'] = pd.to_datetime(single_measures_df['date'])
    single_measures_df['weekday'] = single_measures_df['date'].dt.day_name()
    print(single_measures_df)
    single_measures_df.to_csv("predict_stock_prices.csv")


    #prepare the dataset for prediction
    #Drop Na values
    single_measures_df = single_measures_df.dropna()
    #reset index
    single_measures_df.reset_index(inplace=True)
    df = df.drop(columns=['index','Unnamed: 0','date','company','end_day_target_value','buy_price','ticker'])

main()