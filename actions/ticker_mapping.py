import pandas as pd

def get_ticker_mapping():
    df = pd.read_csv('stock_data/nasdaq_screener.csv')
    ticker_mapping = {}

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Convert company name to lowercase for case-insensitive comparison
        company_name = row['Name'].lower()

        # Iterate through each word in the company name
        for word in company_name.split():
            # Check if the word is contained within the company name
            if word in company_name:
                # If a partial match is found, add it to the mapping
                ticker_mapping[word] = row['Symbol']

        # Convert the 'Symbol' column value to lowercase if it's a string
        symbol = row['Symbol']
        if isinstance(symbol, str):
            # Check if the symbol can be lowered (ignoring non-string values)
            try:
                lowered_symbol = symbol.lower()
            except AttributeError:
                lowered_symbol = None
                
            if lowered_symbol:
                # If the symbol can be lowered, add it to the mapping
                for word in lowered_symbol.split():
                    ticker_mapping[word] = symbol

    return ticker_mapping
