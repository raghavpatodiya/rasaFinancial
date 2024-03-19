import requests
import pandas as pd
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os  # to get env
from dotenv import load_dotenv

load_dotenv()  # taking environment variables from .env file
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


class ActionGetMarketStatus(Action):
    def name(self) -> Text:
        return "get_market_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # debug statement
            region = next(tracker.get_latest_entity_values("region"), None).lower()
            print(region) # debug statement
            url = f"https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            
            if region in ['united states', 'canada', 'united kingdom', 'germany', 'france', 'spain', 'portugal',
                          'japan', 'india', 'mainland china', 'hong kong', 'brazil', 'mexico', 'south africa', 'global']:
                # Find the market data for the specified region
                for market in data['markets']:
                    if market['region'].lower() == region:
                        message = f"Region: {market['region']}\n"
                        message += f"Market Type: {market['market_type']}\n"
                        message += f"Primary Exchanges: {market['primary_exchanges']}\n"
                        message += f"Local Open: {market['local_open']}\n"
                        message += f"Local Close: {market['local_close']}\n"
                        message += f"Current Status: {market['current_status']}\n"
                        message += f"Notes: {market['notes']}"
                        dispatcher.utter_message(text=message)
                        # break  # Stop searching once the target region is found         
            else:
                dispatcher.utter_message(text=f"Region {region} is not supported.")
        

        except Exception as e:
            url = f"https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            region = 'global'
            for market in data['markets']:
                    if market['region'].lower() == region:
                        message = f"Region: {market['region']}\n"
                        message += f"Market Type: {market['market_type']}\n"
                        message += f"Primary Exchanges: {market['primary_exchanges']}\n"
                        message += f"Local Open: {market['local_open']}\n"
                        message += f"Local Close: {market['local_close']}\n"
                        message += f"Current Status: {market['current_status']}\n"
                        message += f"Notes: {market['notes']}"
                        dispatcher.utter_message(text=message)
            # dispatcher.utter_message(text=f"An error occurred: {e}")

        return []


