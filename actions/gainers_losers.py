import requests
import pandas as pd
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# check out https://www.alphavantage.co/documentation/#

import os # to get env
from dotenv import load_dotenv
load_dotenv() # taking environment variables from .env file
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class ActionGetTopStocks(Action):
    def name(self) -> Text:
        return "get_top_stock"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()

            # extract the top-performing stocks from the response
            if 'top_gainers' in data:
                top_gainers = data['top_gainers']
                top_5_gainers = top_gainers[:5]

                message = "Here are the top gainers:\n"
                for stock in top_5_gainers:
                    message += f"- {stock['ticker']}: {stock['change_percentage']}\n"

                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Unable to fetch top gainers at the moment. Please try again later.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []

class ActionGetWorstStocks(Action):
    def name(self) -> Text:
        return "get_worst_stock"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if 'top_losers' in data:
                top_losers = data['top_losers']
                top_5_losers = top_losers[:5]

                message = "Here are the top losers:\n"
                for stock in top_5_losers:
                    message += f"- {stock['ticker']}: {stock['change_percentage']}\n"

                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Unable to fetch top gainers at the moment. Please try again later.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []