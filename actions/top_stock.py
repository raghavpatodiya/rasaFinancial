import requests
import pandas as pd
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os # to get env
from dotenv import load_dotenv
load_dotenv() # taking environment variables from .env file
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class ActionGetTopStocks(Action):
    def name(self) -> Text:
        return "get_top_stock"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            api_key = "ALPHA_VANTAGE_API_KEY"
            url = f"https://www.alphavantage.co/query?function=SECTOR&apikey={api_key}"
            response = requests.get(url)
            data = response.json()

            # Extract the top-performing stocks from the response
            if 'Rank A: Real-Time Performance' in data:
                top_stocks = data['Rank A: Real-Time Performance']
                top_5_stocks = top_stocks[:5]

                message = "Here are the top performing stocks:\n"
                for stock_name, performance in top_5_stocks.items():
                    message += f"- {stock_name}: {performance}%\n"

                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Unable to fetch top stocks at the moment. Please try again later.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []

