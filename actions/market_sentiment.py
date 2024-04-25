import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker

import os
from dotenv import load_dotenv

load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class ActionGetMarketSentiment(Action):
    def name(self) -> Text:
        return "get_market_sentiment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            if company_name:
                company_name = company_name.lower()
            else:
                company_name = tracker.get_slot("stock_name")
            self.process_market_sentiment(dispatcher, company_name)
        
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message(text="Sorry, I encountered an error while processing your request.")

        return []

    def process_market_sentiment(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        
        if stock_ticker:    
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={stock_ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
            response = requests.get(url)
            data = response.json()
            print(data)
            if 'feed' in data:
                sentiment_scores = [float(entry.get('overall_sentiment_score', 0)) for entry in data['feed']]
                
                if sentiment_scores:
                    average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                    sentiment_label = self.get_sentiment_label(average_sentiment)
                    dispatcher.utter_message(text=f"The market sentiment for {company_name} is {sentiment_label}")
                else:
                    dispatcher.utter_message(text="No sentiment data available for this company.")
            else:
                dispatcher.utter_message(text="No sentiment data available for this company.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find the stock ticker for that company.")
    
    def get_sentiment_label(self, sentiment_score: float) -> str:
        if sentiment_score <= -0.35:
            return 'Bearish'
        elif -0.35 < sentiment_score <= -0.15:
            return 'Somewhat-Bearish'
        elif -0.15 < sentiment_score < 0.15:
            return 'Neutral'
        elif 0.15 <= sentiment_score < 0.35:
            return 'Somewhat-Bullish'
        else:
            return 'Bullish'
