from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yfinance as yf

class ActionGetStockPrice(Action):
    def name(self) -> Text:
        return "get_stock_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ticker_mapping = {
            "tesla": "TSLA",
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "amazon": "AMZN",
            "facebook": "FB",
            "twitter": "TWTR",
            "netflix": "NFL",
            "instagram": "INST",
            "snapchat": "SNAP",
            "uber": "UBER",
            "lyft": "LYFT",
            "airbnb": "AIRBNB",
            "disney": "DIS",
            "walmart": "WMT",
            "nike": "NKE",
            "coca-cola": "KO",
            "pepsi": "PEP",
            "mastercard": "MASTER"
        }
        try:
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            if company_name.lower() in ticker_mapping:
                stock_ticker = ticker_mapping[company_name.lower()]
                stock_data = yf.Ticker(stock_ticker)
                if len(stock_data.history(period='1d')) > 0:
                    current_price = stock_data.history(period='1d')['Close'][0]
                    dispatcher.utter_message(text=f"The current stock price of {stock_ticker} is ${current_price:.2f}")
                else:
                    dispatcher.utter_message(text=f"No data found for the stock symbol {stock_ticker}. Please enter a valid stock symbol.")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            print(f"An error occurred while fetching stock price: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")

        return []
