import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker_mapping

import os  # to get env
from dotenv import load_dotenv

load_dotenv()  # taking environment variables from .env file
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class ActionGetMarketSentiment(Action):
    def name(self) -> Text:
        return "get_market_sentiment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            self.process_market_sentiment(dispatcher, company_name)
        
        except Exception as e:
            company_name=tracker.get_slot("stock_name")
            self.process_market_sentiment(dispatcher, company_name)

        return []

    def process_market_sentiment(self, dispatcher: CollectingDispatcher, company_name: str):
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            # Get the stock ticker symbol using ticker mapping
            stock_ticker = ticker_mapping[company_name]

            if stock_ticker:    
                # Query Alpha Vantage API for news sentiment data
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
        else:
            dispatcher.utter_message(text="Please specify the name of the company you want to know the market sentiment for.")
    
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
