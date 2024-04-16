from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import yfinance as yf
import json

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
            currency = data.get("currency")

            if predicted_price is not None and current_price is not None:
                price_change = current_price - predicted_price
                price_change_percentage = (price_change / current_price) * 100
                if predicted_price > current_price:
                    dispatcher.utter_message(text=f"Recommendation: Buy. Predicted price: {predicted_price:.2f} {currency}, Current price: {current_price:.2f} {currency}")
                elif predicted_price < current_price and price_change_percentage > 10:
                    dispatcher.utter_message(text=f"Recommendation: Sell. Predicted price: {predicted_price:.2f} {currency}, Current price: {current_price:.2f} {currency}")
                else:
                    dispatcher.utter_message(text=f"Recommendation: Hold. Predicted price: {predicted_price:.2f} {currency}, Current price: {current_price:.2f} {currency}")
            else:
                dispatcher.utter_message(text="Unable to determine buy/sell/hold recommendation. Please try again later.")
        
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []