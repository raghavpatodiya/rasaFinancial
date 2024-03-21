import requests
import pandas as pd
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker_mapping
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import yfinance as yf
import json

class ActionGetStockPredictions(Action):
    def name(self) -> Text:
        return "get_stock_predictions"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            ticker_mapping = get_ticker_mapping()

            if company_name in ticker_mapping:
                stock_ticker = ticker_mapping[company_name]
                stock_data = yf.Ticker(stock_ticker)
                current_price = stock_data.history(period='1d')['Close'].iloc[0]
                df = self.fetch_historical_data(stock_ticker)
                model, X_test, y_test = self.build_predictive_model(df)
                mse = self.backtest_model(model, X_test, y_test)

                if model:
                    predicted_price = self.predict_stock_price(model, df)

                    self.store_prediction(company_name, stock_ticker, predicted_price, current_price)

                    dispatcher.utter_message(text=f"The predicted stock price for {company_name} is ${predicted_price:.2f}. Mean Squared Error: {mse:.2f}")
                else:
                    dispatcher.utter_message(text="Not enough data to build a predictive model.")

            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            company_name = tracker.get_slot("stock_name").lower()
            ticker_mapping = get_ticker_mapping()

            if company_name in ticker_mapping:
                stock_ticker = ticker_mapping[company_name]
                stock_data = yf.Ticker(stock_ticker)
                current_price = stock_data.history(period='1d')['Close'].iloc[0]
                df = self.fetch_historical_data(stock_ticker)
                model, X_test, y_test = self.build_predictive_model(df)
                mse = self.backtest_model(model, X_test, y_test)

                if model:
                    predicted_price = self.predict_stock_price(model, df)

                    self.store_prediction(company_name, stock_ticker, predicted_price, current_price)

                    dispatcher.utter_message(text=f"The predicted stock price for {company_name} is ${predicted_price:.2f}. Mean Squared Error: {mse:.2f}")
                else:
                    dispatcher.utter_message(text="Not enough data to build a predictive model.")

            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")

        return []

    def fetch_historical_data(self, stock_ticker: str) -> pd.DataFrame:
        stock_data = yf.Ticker(stock_ticker)
        df = stock_data.history(period="max")  # Fetch historical data for all available dates
        print("Columns available in the DataFrame:")
        print(df.columns)
        return df

    def build_predictive_model(self, df: pd.DataFrame) -> LinearRegression:
        if not df.empty:
            features = ['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits']
            X = df[features]  
            y = df['Close']  
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)   
            model = LinearRegression()
            model.fit(X_train, y_train)

            # # Evaluate model
            # y_pred_train = model.predict(X_train)
            # y_pred_test = model.predict(X_test)
            # mse_train = mean_squared_error(y_train, y_pred_train)
            # mse_test = mean_squared_error(y_test, y_pred_test)
            # mae_train = mean_absolute_error(y_train, y_pred_train)
            # mae_test = mean_absolute_error(y_test, y_pred_test)
            # r2_train = r2_score(y_train, y_pred_train)
            # r2_test = r2_score(y_test, y_pred_test)

            # # Print evaluation metrics
            # print("Training set evaluation:")
            # print(f"Mean Squared Error (MSE): {mse_train:.2f}")
            # print(f"Mean Absolute Error (MAE): {mae_train:.2f}")
            # print(f"R-squared (R2): {r2_train:.2f}")
            # print("\nTesting set evaluation:")
            # print(f"Mean Squared Error (MSE): {mse_test:.2f}")
            # print(f"Mean Absolute Error (MAE): {mae_test:.2f}")
            # print(f"R-squared (R2): {r2_test:.2f}")

            return model, X_test, y_test
            
        else:
            return None, None, None

    def backtest_model(self, model: LinearRegression, X_test: pd.DataFrame, y_test: pd.Series) -> float:
        if model and X_test is not None and y_test is not None:
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            return mse
        else:
            return float('inf')

    def predict_stock_price(self, model: LinearRegression, df: pd.DataFrame) -> float:
        current_data = df.iloc[-1]
        predicted_price = model.predict(current_data[['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits']].values.reshape(1, -1))[0]
        return predicted_price

    def store_prediction(self, company_name: str, stock_ticker: str, predicted_price: float, current_price: float) -> None:
        data = {
            "company_name": company_name,
            "stock_ticker": stock_ticker,
            "predicted_price": predicted_price,
            "current_price": current_price
        }
        with open('stock_data.json', 'w') as file:
            json.dump(data, file)

class ActionBuySellHold(Action):
    def name(self) -> Text:
        return "get_buy_sell_hold"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Retrieve data from external storage
            with open('stock_data.json', 'r') as file:
                data = json.load(file)
            # Extract predicted and current prices
            predicted_price = data.get("predicted_price")
            current_price = data.get("current_price")

            if predicted_price is not None and current_price is not None:
                price_change = current_price - predicted_price
                price_change_percentage = (price_change / current_price) * 100
                if predicted_price > current_price:
                    dispatcher.utter_message(text=f"Recommendation: Buy. Predicted price: ${predicted_price:.2f}, Current price: ${current_price:.2f}")
                elif predicted_price < current_price and price_change_percentage > 10:
                    dispatcher.utter_message(text=f"Recommendation: Sell. Predicted price: ${predicted_price:.2f}, Current price: ${current_price:.2f}")
                else:
                    dispatcher.utter_message(text=f"Recommendation: Hold. Predicted price: ${predicted_price:.2f}, Current price: ${current_price:.2f}")
            else:
                dispatcher.utter_message(text="Unable to determine buy/sell/hold recommendation. Please try again later.")
        
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []
    



  