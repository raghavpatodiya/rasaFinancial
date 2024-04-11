import yfinance as yf
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

def get_stock_data(symbol):
    stock_data = yf.Ticker(symbol)
    return stock_data.history(period="max")

def preprocess_data(df):
    df.dropna(inplace=True)
    features = ['Open', 'High', 'Low', 'Volume', 'Close']
    df = df[features]
    return df

def train_model(df):
    df['Target'] = df['Close'].shift(-30)
    df.dropna(inplace=True)
    X = df.drop(columns=['Target'])
    y = df['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBRegressor(objective ='reg:squarederror', n_estimators=100)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    print("Mean Squared Error:", mse)
    
    return model

def plot_predicted_prices(model, df):
    future_dates = pd.date_range(start=df.index[-1], periods=30)
    future_dates = future_dates.tz_convert(df.index.tz)
    future_features = np.repeat(df.iloc[-1][:-1].values.reshape(1, -1), 30, axis=0) 
    future_prices = model.predict(future_features)
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Actual Prices')
    plt.plot(future_dates, future_prices, label='Predicted Prices')
    plt.xlabel('Date')
    plt.ylabel('Close Price in $')
    plt.title('Predicted Stock Prices for the Next 30 Days')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

def main():
    symbol = 'AAPL'
    df = get_stock_data(symbol)
    df = preprocess_data(df)
    model = train_model(df)
    plot_predicted_prices(model, df)

if __name__ == "__main__":
    main()
