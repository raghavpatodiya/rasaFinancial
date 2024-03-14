import pandas as pd
import re

# def preprocess_company_name(company_name):
#     # Convert to lowercase
#     company_name = company_name.lower()
#     # Remove whitespaces, ',', '.', and '-'
#     company_name = re.sub(r'[\s,.-]', '', company_name)
#     return company_name

# def get_ticker_mapping(): 
#     df = pd.read_excel('stock_data/stock_tickers.xlsx')
#     ticker_mapping = dict(zip(map(preprocess_company_name, df['Company Name']), df['Symbol']))
#     return ticker_mapping


def get_ticker_mapping(): 
    df = pd.read_excel('stock_data/stock_tickers.xlsx')
    ticker_mapping = dict(zip(df['Company Name'].str.lower(), df['Symbol']))
    return ticker_mapping