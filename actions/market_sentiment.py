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
                    if 'overall_sentiment_score'  in data:
                        sentiment_scores = [float(item['overall_sentiment_score']) for item in data if 'overall_sentiment_score' in item]
                        if sentiment_scores:
                            average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                            sentiment_label = ''
                            if average_sentiment <= -0.35:
                                sentiment_label = 'Bearish'
                            elif -0.35 < average_sentiment <= -0.15:
                                sentiment_label = 'Somewhat-Bearish'
                            elif -0.15 < average_sentiment < 0.15:
                                sentiment_label = 'Neutral'
                            elif 0.15 <= average_sentiment < 0.35:
                                sentiment_label = 'Somewhat-Bullish'
                            else:
                                sentiment_label = 'Bullish'

                            dispatcher.utter_message(text=f"The market sentiment for {company_name} is {sentiment_label}")
                        else:
                            dispatcher.utter_message(text="No sentiment data available for this company.")
                    else:
                        dispatcher.utter_message(text="overall_sentiment_scores couldn't be extracted")
                else:
                    dispatcher.utter_message(text="Sorry, I couldn't find the stock ticker for that company.")
            else:
                dispatcher.utter_message(text="Please specify the name of the company you want to know the market sentiment for.")
        
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")

        return []
