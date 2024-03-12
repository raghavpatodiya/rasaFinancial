import requests
import pandas as pd
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker_mapping
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
class ActionGetStockPredictions(Action):
    def name(self) -> Text:
        return "get_stock_predictions"

    def fetch_historical_data(self, stock_ticker: str) -> pd.DataFrame:
        endpoint = 'https://api.twelvedata.com/time_series'
        params = {
            'symbol': stock_ticker,
            'interval': '1day',  # Adjust interval as needed
            'outputsize': 1000,  # Adjust output size as needed
            'apikey': self.api_key
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        if 'values' in data:
            df = pd.DataFrame(data['values'])
        else:
            df = pd.DataFrame()
        return df

    def build_predictive_model(self, df: pd.DataFrame) -> LinearRegression:
        if not df.empty:
            # Prepare data for modeling
            X = df[['open', 'high', 'low', 'volume']]  # Features
            y = df['close']  # Target variable
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)   
            model = LinearRegression()
            model.fit(X_train, y_train)
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

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            with open('actions/API_KEY.txt', 'r') as file:
                self.api_key = file.read().strip()

            entities = tracker.latest_message.get('entities', [])
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            ticker_mapping = get_ticker_mapping()

            if company_name in ticker_mapping:
                stock_ticker = ticker_mapping[company_name]

                df = self.fetch_historical_data(stock_ticker)
                model, X_test, y_test = self.build_predictive_model(df)
                mse = self.backtest_model(model, X_test, y_test)

                if model:
                    current_data = df.iloc[-1]
                    prediction = model.predict(current_data[['open', 'high', 'low', 'volume']].values.reshape(1, -1))[0]
                    dispatcher.utter_message(text=f"The predicted stock price for {company_name} is ${prediction:.2f}. Mean Squared Error: {mse:.2f}")
                else:
                    dispatcher.utter_message(text="Not enough data to build a predictive model.")

            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []
