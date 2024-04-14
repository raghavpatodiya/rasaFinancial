from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker
from typing import Any, Text, Dict, List
import yfinance as yf
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Add the new action class here
class ActionGetPredictionsGraph(Action):
    def name(self) -> Text:
        return "get_predictions_graph" 
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # entities = tracker.latest_message.get('entities', [])
            # print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            if company_name:
                company_name = company_name.lower()
            else:
                company_name = tracker.get_slot("stock_name").lower()
            print("Company name extracted:", company_name)  # Debug statement
            stock_ticker = get_ticker(company_name)
            stock_data = yf.Ticker(stock_ticker)
            df = stock_data.history(period="max")
            df = self.preprocess_data(df)
            model = self.train_model(df)
            self.plot_predicted_prices(model, df, dispatcher)
        
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message(text="Sorry, I encountered an error while processing your request.")

        return []

    def preprocess_data(self, df):
        df.dropna(inplace=True)
        features = ['Open', 'High', 'Low', 'Volume', 'Close']
        df = df[features]
        return df

    def train_model(self, df):
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

    def plot_predicted_prices(self, model, df, dispatcher: CollectingDispatcher):
        last_30_days = df[-30:]  # Selecting only the last 30 days of historical data
        future_dates = pd.date_range(start=last_30_days.index[-1], periods=30, freq='B')  # Business days
        future_dates = future_dates.tz_convert(df.index.tz)
        future_features = np.repeat(last_30_days.iloc[-1][:-1].values.reshape(1, -1), 30, axis=0) 
        future_prices = model.predict(future_features)
        
        plt.figure(figsize=(12, 6))
        plt.plot(last_30_days.index, last_30_days['Close'], label='Last 30 Days Prices', color='blue')
        plt.plot(future_dates, future_prices, label='Predicted Prices', color='red')  # Plot predicted prices
        plt.xlabel('Date')
        plt.ylabel('Close Price in $')
        plt.title('Predicted Stock Prices for the Next 30 Days')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        predictions_plot_file = 'static/images/predicted_stock_graph.png'
        plt.savefig(predictions_plot_file)
        plt.close()
        dispatcher.utter_message(image=predictions_plot_file)
