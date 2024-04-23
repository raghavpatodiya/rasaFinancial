from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker
import yfinance as yf
import requests
from datetime import datetime, timedelta
from automation_script  import inr_to_usd

import os 
from dotenv import load_dotenv

load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class ActionGetComparison(Action):
    def name(self) -> Text:
        return "get_comparison"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            if company_name:
                company_name = company_name.lower()
            else:
                company_name = tracker.get_slot("stock_name")

            company_name2 = next(tracker.get_latest_entity_values("stock_name2"), None)
            if company_name2:
                company_name2 = company_name2.lower()
            else:
                company_name2 = tracker.get_slot("stock_name2")

            info = next(tracker.get_latest_entity_values("info"), None).lower()
            print("Company names extracted:", company_name, company_name2)  # Debug statement
            print("Info extracted:", info)  # Debug statement
            
            if info:
                info = info.lower()
                self.process_comparison(dispatcher, company_name, company_name2, info)
            else:
                dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")
        
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message(text="Sorry, I encountered an error while processing your request.")

        return []

    def process_comparison(self, dispatcher, company_name, company_name2, info):
        if info in ["price", "prices", "stock price", "stock"]:
            self.compare_stock_price(dispatcher, company_name, company_name2)
        elif info in ["market sentiment", "sentiment", "sentiments", "market sentiments"]:
            self.compare_market_sentiment(dispatcher, company_name, company_name2)
        elif info in ["volatility", "volatile"]:
            self.compare_volatility(dispatcher, company_name, company_name2)
        elif info in ["trend", "trends"]:
            self.compare_stock_trend(dispatcher, company_name, company_name2)
        elif info in ["market cap", "market capitalization", "mkt cap", "capital"]:
            self.compare_market_cap(dispatcher, company_name, company_name2)
        elif info in ["revenue", "earnings", "profit", "income", "net income", "net profit"]:
            self.compare_revenue(dispatcher, company_name, company_name2)
        elif info in ["eps", "earnings per share", "earning per share", "earn per share"]:
            self.compare_eps(dispatcher, company_name, company_name2)
        elif info in ["pe", "p/e", "price to earnings", "price to earning", "pe ratio", "p/e ratio"]:
            self.compare_pe_ratio(dispatcher, company_name, company_name2)
        elif info in ["roe", "return on equity"]:
            self.compare_roe(dispatcher, company_name, company_name2)
        elif info in ["gross margin", "margin", "gm", "gross margins", "margins"]:
            self.compare_gross_margins(dispatcher, company_name, company_name2)
        elif info in ["debt to equity", "dte ratio", "dte"]:
            self.compare_dte_ratio(dispatcher, company_name, company_name2)
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")

    def compare_stock_price(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        current_price = self.process_stock_price(company_name)
        current_price2 = self.process_stock_price(company_name2)

        if current_price is not None and current_price2 is not None:
            if current_price > current_price2:
                dispatcher.utter_message(text=f"The current stock price of {company_name} ({current_price:.2f} USD) is higher than {company_name2} ({current_price2:.2f} USD).")
            elif current_price < current_price2:
                dispatcher.utter_message(text=f"The current stock price of {company_name} ({current_price:.2f} USD) is lower than {company_name2} ({current_price2:.2f} USD).")
            else:
                dispatcher.utter_message(text=f"The current stock prices of {company_name} and {company_name2} are equal ({current_price:.2f} USD).")
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

        formatted_market_cap = self.format_amount(market_cap)
        formatted_market_cap2 = self.format_amount(market_cap2)

        if market_cap is not None and market_cap2 is not None:
            if market_cap > market_cap2:
                dispatcher.utter_message(text=f"The market cap of {company_name} ({formatted_market_cap} USD) is higher than {company_name2} ({formatted_market_cap2} USD).")
            elif market_cap < market_cap2:
                dispatcher.utter_message(text=f"The market cap of {company_name} ({formatted_market_cap} USD) is lower than {company_name2} ({formatted_market_cap2} USD).")
            else:
                dispatcher.utter_message(text=f"The market caps of {company_name} and {company_name2} are equal ({formatted_market_cap} USD).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve market cap data for one or both of the companies.")

    def compare_revenue(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        revenue = self.process_revenue(company_name)
        revenue2 = self.process_revenue(company_name2)

        formatted_revenue = self.format_amount(revenue)
        formatted_revenue2 = self.format_amount(revenue2)

        if revenue is not None and revenue2 is not None:
            if revenue > revenue2:
                dispatcher.utter_message(text=f"The revenue of {company_name} ({formatted_revenue} USD) is higher than {company_name2} ({formatted_revenue2} USD).")
            elif revenue < revenue2:
                dispatcher.utter_message(text=f"The revenue of {company_name} ({formatted_revenue} USD) is lower than {company_name2} ({formatted_revenue2} USD).")
            else:
                dispatcher.utter_message(text=f"The revenue of {company_name} and {company_name2} are equal ({formatted_revenue} USD).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve revenue data for one or both of the companies.")

    def compare_eps(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        eps = self.process_eps(company_name)
        eps2 = self.process_eps(company_name2)

        if eps is not None and eps2 is not None:
            if eps > eps2:
                dispatcher.utter_message(text=f"The EPS of {company_name} ({eps} USD) is higher than {company_name2} ({eps2} USD).")
            elif eps < eps2:
                dispatcher.utter_message(text=f"The EPS of {company_name} ({eps} USD) is lower than {company_name2} ({eps2} USD).")
            else:
                dispatcher.utter_message(text=f"The EPSs of {company_name} and {company_name2} are equal ({eps} USD).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve EPS data for one or both of the companies.")

    def compare_pe_ratio(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        pe_ratio = self.process_pe_ratio(company_name)
        pe_ratio2 = self.process_pe_ratio(company_name2)

        pe_ratio = "{:.2f}".format(pe_ratio)
        pe_ratio2 = "{:.2f}".format(pe_ratio2)

        if pe_ratio is not None and pe_ratio2 is not None:
            if pe_ratio > pe_ratio2:
                dispatcher.utter_message(text=f"The PE ratio of {company_name} ({pe_ratio}) is higher than {company_name2} ({pe_ratio2}).")
            elif pe_ratio < pe_ratio2:
                dispatcher.utter_message(text=f"The PE ratio of {company_name} ({pe_ratio}) is lower than {company_name2} ({pe_ratio2}).")
            else:
                dispatcher.utter_message(text=f"The PE ratios of {company_name} and {company_name2} are equal ({pe_ratio}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve PE ratio data for one or both of the companies.")

    def compare_roe(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        roe = self.process_roe(company_name)
        roe2 = self.process_roe(company_name2)

        roe = "{:.4f}".format(roe)
        roe2 = "{:.4f}".format(roe2)

        if roe is not None and roe2 is not None:
            if roe > roe2:
                dispatcher.utter_message(text=f"The ROE of {company_name} ({roe}) is higher than {company_name2} ({roe2}).")
            elif roe < roe2:
                dispatcher.utter_message(text=f"The ROE of {company_name} ({roe}) is lower than {company_name2} ({roe2}).")
            else:
                dispatcher.utter_message(text=f"The ROEs of {company_name} and {company_name2} are equal ({roe}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve ROE data for one or both of the companies.")

    def compare_gross_margins(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        gross_margins = self.process_gross_margins(company_name)
        gross_margins2 = self.process_gross_margins(company_name2)

        gross_margins = "{:.4f}".format(gross_margins)
        gross_margins2 = "{:.4f}".format(gross_margins2)

        if gross_margins is not None and gross_margins2 is not None:
            if gross_margins > gross_margins2:
                dispatcher.utter_message(text=f"The gross margins of {company_name} ({gross_margins}) is higher than {company_name2} ({gross_margins2}).")
            elif gross_margins < gross_margins2:
                dispatcher.utter_message(text=f"The gross margins of {company_name} ({gross_margins}) is lower than {company_name2} ({gross_margins2}).")
            else:
                dispatcher.utter_message(text=f"The gross margins of {company_name} and {company_name2} are equal ({gross_margins}).")
        else: 
            dispatcher.utter_message(text="Sorry, couldn't retrieve gross margins data for one or both of the companies.")

    def compare_dte_ratio(self, dispatcher: CollectingDispatcher, company_name: str, company_name2: str):
        dte_ratio = self.process_dte_ratio(company_name)
        dte_ratio2 = self.process_dte_ratio(company_name2)

        dte_ratio = "{:.2f}".format(dte_ratio)
        dte_ratio2 = "{:.2f}".format(dte_ratio2)

        if dte_ratio is not None and dte_ratio2 is not None:
            if dte_ratio > dte_ratio2:
                dispatcher.utter_message(text=f"The DTE ratio of {company_name} ({dte_ratio}) is higher than {company_name2} ({dte_ratio2}).")
            elif dte_ratio < dte_ratio2:
                dispatcher.utter_message(text=f"The DTE ratio of {company_name} ({dte_ratio}) is lower than {company_name2} ({dte_ratio2}).")
            else:
                dispatcher.utter_message(text=f"The DTE ratios of {company_name} and {company_name2} are equal ({dte_ratio}).")
        else:
            dispatcher.utter_message(text="Sorry, couldn't retrieve DTE ratio data for one or both of the companies.")
    
    def process_stock_price(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        
        if len(stock_data.history(period='1d')) > 0:
            current_price = stock_data.history(period='1d')['Close'].iloc[0]
            if stock_ticker.endswith(".NS"):
                current_price = inr_to_usd(current_price)
            return current_price
        else:
            return None
        
    def process_sentiment_score(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
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

    def process_volatility(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        df = stock_data.history(period="1mo")

        if not df.empty:
            volatility = df['Close'].pct_change().std() * (252**0.5) 
            return volatility
        else:
            return None

    def process_stock_trend(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        df = stock_data.history(period="1wk")

        if not df.empty:
            price_change_percentage = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            return price_change_percentage
        else:
            return None

    def process_market_cap(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        market_cap = stock_data.info['marketCap']

        if stock_ticker.endswith(".NS"):
                market_cap = inr_to_usd(market_cap)
        return market_cap
        
    def process_revenue(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        revenue = stock_data.info['totalRevenue']

        if stock_ticker.endswith(".NS"):
                revenue = inr_to_usd(revenue)
        return revenue
                
    def process_eps(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        eps = stock_data.info['trailingEps']

        if stock_ticker.endswith(".NS"):
                eps = inr_to_usd(eps)
        return eps

    def process_pe_ratio(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        pe_ratio = stock_data.info['trailingPE']
        return pe_ratio
    
    def process_roe(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        roe = stock_data.info['returnOnEquity']
        return roe

    def process_gross_margins(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        gross_margins = stock_data.info['grossMargins']
        return gross_margins

    def process_dte_ratio(self, company_name: str) -> float:
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        dte_ratio = stock_data.info['debtToEquity']
        return dte_ratio

    def format_amount(self, amount: str) -> str:
        if amount != 'N/A':
            amount_numeric = float(amount)
            if amount_numeric >= 1e12:
                formatted_amount = f"{amount_numeric / 1e12:.2f} T"
            elif amount_numeric >= 1e9:
                formatted_amount = f"{amount_numeric / 1e9:.2f} B"
            elif amount_numeric >= 1e6:
                formatted_amount = f"{amount_numeric / 1e6:.2f} M"
            else:
                formatted_amount = f"{amount_numeric:.2f}"
        else:
            formatted_amount = 'N/A'
        return formatted_amount
