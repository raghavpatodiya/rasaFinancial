import pandas as pd

def get_ticker_mapping():
    df = pd.read_csv('stock_data/nasdaq_screener.csv')
    ticker_mapping = {}

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Convert company name to lowercase for case-insensitive comparison
        company_name = row['Name'].lower()

        # Iterate through each word in the user input
        for word in company_name.split():
            # Check if the word is contained within the company name
            if word in company_name:
                # If a partial match is found, add it to the mapping
                ticker_mapping[word] = row['Symbol']
    
    return ticker_mapping
