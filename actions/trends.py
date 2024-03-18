from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import yfinance as yf
from actions.ticker_mapping import get_ticker_mapping
import json
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
                    price_change_percentage = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
                    if price_change_percentage > 0:
                        dispatcher.utter_message(text=f"The stock price of {company_name} has increased by {price_change_percentage:.2f}%. Trend - Upwards")
                    elif price_change_percentage < 0:
                        dispatcher.utter_message(text=f"The stock price of {company_name} has decreased by {price_change_percentage:.2f}%. Trend - Downwards")
                    else:
                        dispatcher.utter_message(text=f"The stock price of {company_name} has remained unchanged. Trend - Stable")
                else:
                    dispatcher.utter_message(text="Unable to analyze trend. No historical data available.")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            # print(f"An error occurred while fetching stock price: {e}")
            # dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")
            with open('stock_data.json', 'r') as file:
                    data = json.load(file)
            current_price = data.get("current_price")
            predicted_price = data.get("predicted_price")
            company_name = data.get("company_name")
            if current_price is not None and predicted_price is not None:
                price_change_percentage = ((current_price - predicted_price) / predicted_price) * 100
                if price_change_percentage > 0:
                    dispatcher.utter_message(text=f"The stock price of {company_name} has increased by {price_change_percentage:.2f}%. Trend - Upwards")
                elif price_change_percentage < 0:
                    dispatcher.utter_message(text=f"The stock price of {company_name} has decreased by {price_change_percentage:.2f}%. Trend - Downwards")
                else:
                    dispatcher.utter_message(text=f"The stock price of {company_name} has remained unchanged. Trend - Stable")
            else:
                dispatcher.utter_message(text="Unable to determine the trend. Please try again later.")

        return []

# get time period from user, if not extracted take default as 1wk
    

class ActionGetStockVolatility(Action):
    def name(self) -> Text:
        return "get_volatility"
    
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
                df = stock_data.history(period="1mo")  # Fetch historical data for the past month
                if not df.empty:
                    volatility = df['Close'].pct_change().std() * (252**0.5)  # Annualized volatility
                    dispatcher.utter_message(text=f"The volatility of {company_name} stock is {volatility:.2f}%.")
                else:
                    dispatcher.utter_message(text="Unable to analyze volatility. No historical data available.")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            # print(f"An error occurred while fetching stock volatility: {e}")
            # dispatcher.utter_message(text="An error occurred while fetching stock volatility. Please try again later.")
            with open('stock_data.json', 'r') as file:
                    data = json.load(file)
            company_name = data.get("company_name")
            stock_ticker = data.get("stock_ticker")
            stock_data = yf.Ticker(stock_ticker)  # Fetch stock_data using stock_ticker
            df = stock_data.history(period="1mo")  # Fetch historical data for the past month
            if not df.empty:
                volatility = df['Close'].pct_change().std() * (252**0.5)  # Annualized volatility
                dispatcher.utter_message(text=f"The volatility of {company_name} stock is {volatility:.2f}%.")
            else:
                dispatcher.utter_message(text="Unable to analyze volatility. No historical data available.")

        return []