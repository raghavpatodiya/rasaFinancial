import requests
import os 
from dotenv import load_dotenv

load_dotenv()  # taking environment variables from .env file
EXCHANGE_RATE_API_KEY=os.getenv("EXCHANGE_RATE_API_KEY")

def get_exchange_rate():
    api_key = EXCHANGE_RATE_API_KEY  
    base_url = "https://api.exchangerate-api.com/v4/latest/INR"
    response = requests.get(base_url, params={"apikey": api_key})
    if response.status_code == 200:
        data = response.json()
        return data["rates"]["USD"]
    else:
        print("Failed to fetch exchange rate.")
        return None

def inr_to_usd(amount_in_inr):
    exchange_rate = get_exchange_rate()
    if exchange_rate is not None:
        amount_in_usd = amount_in_inr * exchange_rate
        return amount_in_usd
    else:
        return None
    
# amount_in_inr = 1000  # Replace with your desired amount in INR
# amount_in_usd = inr_to_usd(amount_in_inr)
# if amount_in_usd is not None:
#     print(f"{amount_in_inr} INR is equal to {amount_in_usd:.2f} USD")
