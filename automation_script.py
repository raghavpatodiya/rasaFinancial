import os
import time
import yfinance as yf
import requests
from dotenv import load_dotenv

load_dotenv()

def count_lines_of_code(file_path):
    with open(file_path, 'r') as file:
        return sum(1 for line in file if line.strip() and not (line.strip().startswith('#') or line.strip().startswith('//') or line.strip().startswith('<!--') or line.strip().startswith('/*')))

def calculate_loc(root_dir):
    total_loc = 0
    folders = {
        ".py": "actions",
        ".yml": "data",
        ".html": "templates",
        ".css": "static/css",
        ".js": "static/js"
    }
    for ext, folder in folders.items():
        folder_path = os.path.join(root_dir, folder)
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith(ext):
                    file_path = os.path.join(root, file_name)
                    loc = count_lines_of_code(file_path)
                    total_loc += loc
    
    for file_name in os.listdir(root_dir):
        if file_name.endswith(".py") or file_name.endswith(".yml"):
            file_path = os.path.join(root_dir, file_name)
            loc = count_lines_of_code(file_path)
            total_loc += loc
            
    with open("loc.txt", "w") as f:
        f.write(str(total_loc))

def format(amount: str) -> str:
    if amount != 'N/A':
        amount_numeric = float(amount)
        if amount_numeric >= 1e12:
            formatted = f"{amount_numeric / 1e12:.2f} T"
        elif amount_numeric >= 1e9:
            formatted = f"{amount_numeric / 1e9:.2f} B"
        elif amount_numeric >= 1e6:
            formatted = f"{amount_numeric / 1e6:.2f} M"
        else:
            formatted = f"{amount_numeric:.2f}"
    else:
        formatted = 'N/A'
    return formatted

def fetch_stock_data():
    symbols = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'META', 'TEAM', 'NVDA', 'TSLA', 'V', 'LLY', 'INFY.NS']
    all_stock_data = []
    for symbol in symbols:
        try:
            if symbol.endswith(".NS"):
                current_price = inr_to_usd(yf.Ticker(symbol).history(period='1d')['Close'].iloc[0])
                previous_close = inr_to_usd(yf.Ticker(symbol).info['previousClose'])
                market_cap = inr_to_usd(yf.Ticker(symbol).info['marketCap'])
            else:
                current_price = yf.Ticker(symbol).info['currentPrice']
                previous_close = yf.Ticker(symbol).info['previousClose']
                market_cap = yf.Ticker(symbol).info['marketCap']
            stock_data = {
                'symbol': symbol,
                'price': current_price,
                'change': round(previous_close - current_price, 2),
                'percent_change': abs(round((previous_close - current_price) / previous_close * 100, 2)),
                'market_cap': format(market_cap)
            }
            all_stock_data.append(stock_data)
        except Exception as e:
            print(f"Error fetching data for symbol {symbol}: {e}")
    return all_stock_data

def write_to_file(stock_data):
    with open('stock_data.txt', 'w') as file:
        for data in stock_data:
            file.write(f"{data['symbol']},{data['price']:.2f},{data['change']:.2f},{data['percent_change']:.2f},{data['market_cap']} \n")

def get_exchange_rate():
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
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
        return round(amount_in_usd, 2)
    else:
        return None
    
def usd_to_inr(amount_in_usd):
    exchange_rate = get_exchange_rate()
    if exchange_rate is not None:
        amount_in_inr = amount_in_usd / exchange_rate
        return round(amount_in_inr, 2)
    else:
        return None

if __name__ == "__main__":
    root_directory = os.getenv("ROOT_DIRECTORY")
    
    while True:
        calculate_loc(root_directory)
        stock_data = fetch_stock_data()
        write_to_file(stock_data)
        time.sleep(5)
