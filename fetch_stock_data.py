import time
import yfinance as yf
from convert_currency import inr_to_usd

def format(amount: str) -> str:
        if amount != 'N/A':
            amount_numeric = float(amount)
            if amount_numeric >= 1e12:
                # Convert to trillion
                formatted = f"{amount_numeric / 1e12:.2f} Tn"
            elif amount_numeric >= 1e9:
                # Convert to billion
                formatted = f"{amount_numeric / 1e9:.2f} Bn"
            elif amount_numeric >= 1e6:
                # Convert to million
                formatted = f"{amount_numeric / 1e6:.2f} Mn"
            else:
                # Leave as is
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

if __name__ == "__main__":
    while True:
        stock_data = fetch_stock_data()
        write_to_file(stock_data)
        time.sleep(5)
