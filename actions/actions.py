from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yfinance as yf

class ActionGetStockPrice(Action):
    def name(self) -> Text:
        return "get_stock_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Extract the stock name from the user's message
            stock_ticker = next(tracker.get_latest_entity_values("stock_name"), None)

            if stock_ticker:
                # Fetch stock data from Yahoo Finance
                stock_data = yf.Ticker(stock_ticker)
                current_price = stock_data.history(period='1d')['Close'][0]
                
                dispatcher.utter_message(text=f"The current stock price of {stock_ticker} is ${current_price:.2f}")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            print(f"An error occurred while fetching stock price: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")

        return []
