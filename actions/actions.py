from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yfinance as yf
from actions.ticker_mapping import get_ticker_mapping

class ActionGetStockPrice(Action):
    def name(self) -> Text:
        return "get_latest_stock_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            print("Company name extracted:", company_name)  # Debug statement

            ticker_mapping = get_ticker_mapping()
            if company_name.lower() in ticker_mapping:
                stock_ticker = ticker_mapping[company_name.lower()]
                stock_data = yf.Ticker(stock_ticker)
                if len(stock_data.history(period='1d')) > 0:
                    current_price = stock_data.history(period='1d')['Close'][0]
                    dispatcher.utter_message(text=f"The current stock price of {company_name} is ${current_price:.2f}")
                else:
                    dispatcher.utter_message(text=f"No data found for the company {company_name}. Please enter a valid company name .")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            print(f"An error occurred while fetching stock price: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")

        return []
