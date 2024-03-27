from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker_mapping
import yfinance as yf
import requests
from datetime import datetime, timedelta

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
            # entities = tracker.latest_message.get('entities', [])
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            company_name2 = next(tracker.get_latest_entity_values("stock_name2"), None).lower()
            info = next(tracker.get_latest_entity_values("info"), None)
            print("Company names extracted:", company_name, company_name2)  # Debug statement
            print("Info extracted:", info)  # Debug statement
            
            if info:
                info = info.lower()
                self.process_comparison(dispatcher, company_name, company_name2, info)
            else:
                dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")
        
        except Exception as e:
            company_name = tracker.get_slot("stock_name").lower()
            company_name2 = tracker.get_slot("stock_name2").lower()
            print("Company names extracted from slot:", company_name, company_name2)  # Debug statement
            info = next(tracker.get_latest_entity_values("info"), None)
            print("Info extracted:", info)  # Debug statement
            if info:
                info = info.lower()
                self.process_comparison(dispatcher, company_name, company_name2, info)
            else:
                dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")

        return []

    def process_comparison(self, dispatcher, company_name, company_name2, info):
        if info == "price" or info == "prices":
            self.compare_stock_price(dispatcher, company_name, company_name2)
        elif info == "market sentiment" or info == "sentiment":
            self.compare_market_sentiment(dispatcher, company_name, company_name2)
        elif info == "volatility":
            self.compare_volatility(dispatcher, company_name, company_name2)
        elif info == 'trend':
            self.compare_stock_trend(dispatcher, company_name, company_name2)
        elif info == "market cap" or info == "market capitalization" or  info == "mkt cap" or info == "capital":
            self.compare_market_cap(dispatcher, company_name, company_name2)
        elif info == "revenue" or info == "earnings" or info == "profit" or info == "income":
            self.compare_revenue(dispatcher, company_name, company_name2)
        elif info == "eps" or info== "earnings per share" or info == "earning per share":
            self.compare_eps(dispatcher, company_name, company_name2)
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")

    def compare_stock_price(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        current_price = self.process_stock_price(company_name)
        current_price2 = self.process_stock_price(company_name2)
        
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
        average_sentiment = self.process_sentiment_score(company_name)
        average_sentiment2 = self.process_sentiment_score(company_name2)

        if average_sentiment is not None and average_sentiment2 is not None:
            if average_sentiment < average_sentiment2:
                dispatcher.utter_message(text=f"The market sentiment for {company_name} is better than {company_name2}.")
            elif average_sentiment > average_sentiment2:
                dispatcher.utter_message(text=f"The market sentiment for {company_name2} is better than {company_name}.")
            else:
                dispatcher.utter_message(text=f"The market sentiment for {company_name} and {company_name2} are equal.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve market sentiment data for one or both of the companies.")

    def compare_volatility(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        volatility = self.process_volatility(company_name)
        volatility2 = self.process_volatility(company_name2)

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
        trend = self.process_stock_trend(company_name)
        trend2 = self.process_stock_trend(company_name2)

        if trend is not None and trend2 is not None:
            if trend > trend2:
                dispatcher.utter_message(text=f"The price trend of {company_name} is higher than {company_name2}.")
            elif trend < trend2:
                dispatcher.utter_message(text=f"The price trend of {company_name} is lower than {company_name2}.")
            else:
                dispatcher.utter_message(text=f"The price trends of {company_name} and {company_name2} are equal.")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve price trend data for one or both of the companies.")

    def compare_market_cap(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        market_cap = self.process_market_cap(company_name)
        market_cap2 = self.process_market_cap(company_name2)

        if market_cap is not None and market_cap2 is not None:
            if market_cap > market_cap2:
                dispatcher.utter_message(text=f"The market cap of {company_name} ({market_cap}) is higher than {company_name2} ({market_cap2}).")
            elif market_cap < market_cap2:
                dispatcher.utter_message(text=f"The market cap of {company_name} ({market_cap}) is lower than {company_name2} ({market_cap2}).")
            else:
                dispatcher.utter_message(text=f"The market caps of {company_name} and {company_name2} are equal ({market_cap}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve market cap data for one or both of the companies.")

    def compare_revenue(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        revenue = self.process_revenue(company_name)
        revenue2 = self.process_revenue(company_name2)

        if revenue is not None and revenue2 is not None:
            if revenue > revenue2:
                dispatcher.utter_message(text=f"The revenue of {company_name} ({revenue}) is higher than {company_name2} ({revenue2}).")
            elif revenue < revenue2:
                dispatcher.utter_message(text=f"The revenue of {company_name} ({revenue}) is lower than {company_name2} ({revenue2}).")
            else:
                dispatcher.utter_message(text=f"The revenue of {company_name} and {company_name2} are equal ({revenue}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve revenue data for one or both of the companies.")

    def compare_eps(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        eps = self.process_eps(company_name)
        eps2 = self.process_eps(company_name2)

        if eps is not None and eps2 is not None:
            if eps > eps2:
                dispatcher.utter_message(text=f"The EPS of {company_name} (${eps}) is higher than {company_name2} (${eps2}).")
            elif eps < eps2:
                dispatcher.utter_message(text=f"The EPS of {company_name} (${eps}) is lower than {company_name2} (${eps2}).")
            else:
                dispatcher.utter_message(text=f"The EPSs of {company_name} and {company_name2} are equal (${eps}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve EPS data for one or both of the companies.")

    def process_stock_price(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            if len(stock_data.history(period='1d')) > 0:
                current_price = stock_data.history(period='1d')['Close'].iloc[0]
                return current_price
            else:
                return None
        else:
            return None

    def process_sentiment_score(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={stock_ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
            response = requests.get(url)
            data = response.json()
            if 'feed' in data:
                sentiment_scores = [float(entry.get('overall_sentiment_score', 0)) for entry in data['feed']]
                if sentiment_scores:
                    average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                    return average_sentiment
                else:
                    return None
            else:
                return None
        else:
            return None

    def process_volatility(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            df = stock_data.history(period="1mo")
            if not df.empty:
                volatility = df['Close'].pct_change().std() * (252**0.5) 
                return volatility
            else:
                return None
        else:
            return None

    def process_stock_trend(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            df = stock_data.history(period="1wk")
            if not df.empty:
                price_change_percentage = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
                return price_change_percentage
            else:
                return None
        else:
            return None

    def process_market_cap(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            market_cap = stock_data.info['marketCap']
            formatted_market_cap = self.format_amount(market_cap)
            return formatted_market_cap
        else:
            return None

    def process_revenue(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            revenue = stock_data.info['totalRevenue']
            formatted_revenue = self.format_amount(revenue)
            return formatted_revenue
        else:
            return None
        
    def process_eps(self, company_name: str) -> float:
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            eps = stock_data.info['trailingEps']
            return eps
        else:
            return None

    def format_amount(self, amount: str) -> str:
        if amount != 'N/A':
            amount_numeric = float(amount)
            if amount_numeric >= 1e12:
                # Convert to trillion
                formatted_amount = f"${amount_numeric / 1e12:.2f} trillion"
            elif amount_numeric >= 1e9:
                # Convert to billion
                formatted_amount = f"${amount_numeric / 1e9:.2f} billion"
            elif amount_numeric >= 1e6:
                # Convert to million
                formatted_amount = f"${amount_numeric / 1e6:.2f} million"
            else:
                # Leave as is
                formatted_amount = f"${amount_numeric:.2f}"
        else:
            formatted_amount = 'N/A'
        return formatted_amount
