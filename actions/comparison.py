from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker_mapping
import yfinance as yf
import requests

import os  # to get env
from dotenv import load_dotenv

load_dotenv()  # taking environment variables from .env file
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class ActionGetComparison(Action):
    def name(self) -> Text:
        return "get_comparison"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Extracting entities
            entities = tracker.latest_message.get('entities', [])
            company_name = tracker.get_slot("stock_name").lower()
            company_name2 = tracker.get_slot("stock_name2").lower()
            info = next(tracker.get_latest_entity_values("info"), None)

            print("Entities extracted:", entities)  # Debug statement
            print("Company names extracted:", company_name, company_name2)  # Debug statement
            print("Info extracted:", info)  # Debug statement
            
            if info:
                info = info.lower()
                if info == "price":
                    self.compare_stock_price(dispatcher, company_name, company_name2)
                elif info == "market sentiment" or info == "sentiment":
                    self.compare_market_sentiment(dispatcher, company_name, company_name2)
                elif info == "volatility":
                    self.compare_volatility(dispatcher, company_name, company_name2)
                elif info == 'trend':
                    self.compare_stock_trend(dispatcher, company_name, company_name2)
                else:
                    dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")
            else:
                dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")
        
        except Exception as e:
            dispatcher.utter_message(text="An error occurred while processing the comparison request.")

        return []

    def compare_stock_price(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        current_price = self.get_stock_price(company_name)
        current_price2 = self.get_stock_price(company_name2)
        
        if current_price is not None and current_price2 is not None:
            if current_price > current_price2:
                dispatcher.utter_message(text=f"The current stock price of {company_name} (${current_price:.2f}) is higher than {company_name2} (${current_price2:.2f}).")
            elif current_price < current_price2:
                dispatcher.utter_message(text=f"The current stock price of {company_name} (${current_price:.2f}) is lower than {company_name2} (${current_price2:.2f}).")
            else:
                dispatcher.utter_message(text=f"The current stock prices of {company_name} and {company_name2} are equal (${current_price:.2f}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve stock price data for one or both of the companies.")

    def compare_market_sentiment(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        sentiment_score = self.get_sentiment_score(company_name)
        sentiment_score2 = self.get_sentiment_score(company_name2)

        if sentiment_score is not None and sentiment_score2 is not None:
            if sentiment_score < sentiment_score2:
                dispatcher.utter_message(text=f"The market sentiment for {company_name} is better than {company_name2}.")
            elif sentiment_score > sentiment_score2:
                dispatcher.utter_message(text=f"The market sentiment for {company_name2} is better than {company_name}.")
            else:
                dispatcher.utter_message(text=f"The market sentiment for {company_name} and {company_name2} are equal.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve market sentiment data for one or both of the companies.")

    def compare_volatility(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        volatility = self.get_volatility(company_name)
        volatility2 = self.get_volatility(company_name2)

        if volatility is not None and volatility2 is not None:
            if volatility < volatility2:
                dispatcher.utter_message(text=f"The volatility of {company_name} is lower than {company_name2}.")
            elif volatility > volatility2:
                dispatcher.utter_message(text=f"The volatility of {company_name} is higher than {company_name2}.")
            else:
                dispatcher.utter_message(text=f"The volatility of {company_name} and {company_name2} are equal.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve volatility data for one or both of the companies.")
                
    def compare_stock_trend(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        trend = self.get_stock_trend(company_name)
        trend2 = self.get_stock_trend(company_name2)

        if trend is not None and trend2 is not None:
            if trend > trend2:
                dispatcher.utter_message(text=f"The price trend of {company_name} is higher than {company_name2}.")
            elif trend < trend2:
                dispatcher.utter_message(text=f"The price trend of {company_name} is lower than {company_name2}.")
            else:
                dispatcher.utter_message(text=f"The price trends of {company_name} and {company_name2} are equal.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve price trend data for one or both of the companies.")

    def get_stock_price(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            if len(stock_data.history(period='1d')) > 0:
                return stock_data.history(period='1d')['Close'].iloc[0]
            else:
                return None
        else:
            return None

    def get_sentiment_score(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={stock_ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
            response = requests.get(url)
            data = response.json()
            if 'feed' in data:
                sentiment_scores = [float(entry.get('overall_sentiment_score', 0)) for entry in data['feed']]
                if sentiment_scores:
                    return sum(sentiment_scores) / len(sentiment_scores)
                else:
                    return None
            else:
                return None
        else:
            return None

    def get_volatility(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            df = stock_data.history(period="1mo")
            if not df.empty:
                return df['Close'].pct_change().std() * (252**0.5) 
            else:
                return None
        else:
            return None

    def get_stock_trend(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            df = stock_data.history(period="1wk")
            if not df.empty:
                return (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            else:
                return None
        else:
            return None

