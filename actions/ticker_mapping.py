import pandas as pd
def get_ticker_mapping(): 
    df = pd.read_excel('stock_data/stock_tickers.xlsx')
    # Create a mapping dictionary from the DataFrame
    ticker_mapping = dict(zip(df['Company Name'].str.lower(), df['Symbol']))
    return ticker_mapping
