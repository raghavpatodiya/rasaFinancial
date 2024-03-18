from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import yfinance as yf
from actions.ticker_mapping import get_ticker_mapping

class ActionGetStockTrend(Action):
    def name(self) -> Text:
        return "get_stock_trend"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            print("Company name extracted:", company_name)  # Debug statement

            ticker_mapping = get_ticker_mapping()
            if company_name in ticker_mapping:
                stock_ticker = ticker_mapping[company_name]
                stock_data = yf.Ticker(stock_ticker)
                df = stock_data.history(period="1wk")  # Fetch historical data for all available dates
                if not df.empty:
                    price_change = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
                    if price_change > 0:
                        dispatcher.utter_message(text=f"The stock price of {company_name} has increased by {price_change:.2f}%. Trend - Upwards")
                    elif price_change < 0:
                        dispatcher.utter_message(text=f"The stock price of {company_name} has decreased by {price_change:.2f}%. Trend - Downwards")
                    else:
                        dispatcher.utter_message(text=f"The stock price of {company_name} has remained unchanged. Trend - Stable")
                else:
                    dispatcher.utter_message(text="Unable to analyze trend. No historical data available.")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            print(f"An error occurred while fetching stock price: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")

        return []

# get time period from user, if not extracted take default as 1wk