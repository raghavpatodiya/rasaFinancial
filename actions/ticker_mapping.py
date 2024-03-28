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

# def get_ticker():
#     df = pd.read_csv('stock_data/nasdaq_screener.csv')
#     ticker = {}

#     # Iterate through each row in the DataFrame
#     for index, row in df.iterrows():
#         # Convert symbol to string
#         company_name = str(row['Symbol'])

#         # Iterate through each character in the symbol
#         for char in company_name:
#             # Check if the character is alphanumeric
#             if char.isalnum():
#                 # If a valid character is found, add it to the mapping
#                 if char.lower() in ticker:
#                     # If the character already exists, append the symbol
#                     ticker[char.lower()].append(company_name)
#                 else:
#                     # If the character doesn't exist, create a new entry
#                     ticker[char.lower()] = [company_name]

#     return ticker