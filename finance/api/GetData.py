from yahoo_fin import requests
import yfinance as yf
import pandas as pd
import numpy as np
from Global import *

industry_ticker = {
    "Basic Materials": ['BHP','LIN','RIO','CTA-PB','APD','VALE','SCCO','SHW'],
    "HealthCare": ['JNJ', 'UNH', 'NVO', 'LLY', 'MRK', 'ABBV', 'AZN', 'PFE'],
    "Energy": ['XOM','CVX','SHEL','TTE','COP','BP','EQNR','ENB'],
    "Consumer Cyclical": ['AMZN','TSLA','HD','BABA','MCD','NKE','TM','LOW'],
    "Communication Services": ['GOOG','GOOGL','META','DIS','TMUS','CMCSA','VZ','NFLX']
}

def get_company_info(ticker, attribute):
    com_info = yf.Ticker(ticker)
    if attribute == 'all':
        result = com_info.info
    else:
        result = com_info.info[attribute]
    # print(result)
    return result

def get_industry_by_ticker(ticker):
    for x in industry_ticker:
        for tick in industry_ticker[x]:
            if tick == ticker:
                return industry_ticker[x]
    return None

def get_ticker_hst(ticker, period):
    """period Value = 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y"""
    com = yf.Ticker(ticker)
    # url = f"https://finance.yahoo.com/quote/{ticker}/history?p={ticker}"
    df = com.history(period=period)
    df.index = df.index.date
    df = df.reset_index().rename(columns={'index': 'Date'})
    df = df.drop(labels=['Dividends', 'Stock Splits'], axis=1)
    df['Adj Close'] = 0
    # name = 'Final.csv'
    # df.to_csv(DIR + f'{name}', index = False, header = True)
    return df

def get_earnings_history(ticker):
    url = 'https://finance.yahoo.com/calendar/earnings?symbol=' + ticker
    headers = {'User-agent': 'Mozilla/5.0'}

    table = pd.read_html(requests.get(url, headers=headers).text)
    df = table[0]
    df = df.drop('Reported EPS', axis=1)
    df = df.drop('Surprise(%)', axis=1)
    df = df.replace('-', np.nan)
    df = df.dropna()
    for ind in df.index:
        df['Earnings Date'][ind] = df['Earnings Date'][ind][0:12]
        df['Earnings Date'][ind] = pd.to_datetime(df['Earnings Date'][ind]).date()
    df = df.reset_index()
    df['EPS Estimate'] = df['EPS Estimate'].astype(float)
    date = df['Earnings Date'][0].replace(year = df['Earnings Date'][0].year - 5)
    df = df[df['Earnings Date'] > date]
    # name = ticker + '_eps.csv'
    # df.to_csv(DIR + f'{name}', index = False, header = True)
    return df