import time
import yfinance as yf

def fetch_stock_data():
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TEAM', 'NVDA', 'TSLA']
    all_stock_data = []
    for symbol in symbols:
        try:
            stock_info = yf.Ticker(symbol)
            info = stock_info.info
            stock_data = {
                'symbol': symbol,
                'price': info['currentPrice'],
                'change': round(info['previousClose'] - info['currentPrice'], 2),  # Rounded to 2 decimal points
                'percent_change': round((info['previousClose'] - info['currentPrice']) / info['previousClose'] * 100, 2)  # Rounded to 2 decimal points
            }
            all_stock_data.append(stock_data)
        except Exception as e:
            print(f"Error fetching data for symbol {symbol}: {e}")
    return all_stock_data

def write_to_file(stock_data):
    with open('stock_data.txt', 'w') as file:
        for data in stock_data:
            file.write(f"{data['symbol']},{data['price']:.2f},{data['change']:.2f},{data['percent_change']:.2f}\n")

if __name__ == "__main__":
    while True:
        stock_data = fetch_stock_data()
        write_to_file(stock_data)
        time.sleep(5)
