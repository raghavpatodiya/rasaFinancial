import pandas as pd

def get_ticker(company_name):
    df = pd.read_csv('stock_data/nasdaq_screener.csv')
    for index, row in df.iterrows():
        ticker = row['Symbol']
        name = row['Name'].lower()
        if company_name in name.split():
            print(ticker)
            return ticker
        if isinstance(ticker, str):
            try:
                lowered_symbol = ticker.lower()
            except AttributeError:
                lowered_symbol = ticker
                
            if lowered_symbol == company_name:
                print(ticker)
                return ticker
    
# what if company name is more that one word ?