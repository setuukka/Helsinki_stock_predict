import yfinance as yf
import pandas as pd
from datetime import date
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression


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
stocklist2 = ["AFAGR.HE", "RELAIS.HE","SAMPO.HE"]

startdate = '2024-11-06' 
enddate = '2024-11-07'



def generate_complete_datetime_range(start, end, freq='min'):
    """Generates a complete datetime range from start to end with the given frequency."""
    return pd.date_range(start=start, end=end, freq=freq)

def reindex_with_complete_range(df, all_minutes):
    """Reindexes the DataFrame with a complete datetime range, filling missing rows with NaN."""
    return df.reindex(all_minutes)

def forward_fill_missing_values(df):
    """Fills missing values in the DataFrame using forward fill."""
    return df.fillna(method='ffill')

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




def main():
    stock = yf.Ticker("OUT1V.HE")
    # Set start and end times
    start_time = "2024-11-06 10:00:00+02:00"
    end_time = "2024-11-06 10:59:00+02:00"
    date = start_time[:10]
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    next_date = date_obj + timedelta(days = 1)
    next_date = next_date.strftime("%Y-%m-%d")

    stock_data = get_stock_data(stock, date_obj, next_date)
    #Drop unnecessary columns
    stock_data = stock_data.drop(columns=['Dividends','Stock Splits'])
    stock_data.set_index('Datetime', inplace=True)  # Set as index

    # Ensure there is a row for each minute, with missing values forward-filled
    stock_data = ensure_minute_intervals(stock_data, start_time, end_time)

    stock_data = map_percentage_change(stock_data)
    stock_data = set_binary_for_percentage_change(stock_data)

    #Regression of time / price
    x = np.array(stock_data['Datetime']).reshape((-1,1))
    y = np.array(str(stock_data['Close']))
    model = LinearRegression().fit(x,y)
    r_sq = model.score(x,y)
    slope = model.coef_
    print(slope)    


    #print(stock_data)

main()