from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker_mapping
import yfinance as yf
class ActionGetComparison(Action):
    def name(self) -> Text:
        return "get_comparison"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            company_name2 = next(tracker.get_latest_entity_values("stock_name2"), None).lower()
            info = next(tracker.get_latest_entity_values("info"), None)
            print("Company names extracted:", company_name, company_name2)  # Debug statement
            print("Info extracted:", info)  # Debug statement
            
            if info:
                info = info.lower()
                if info == "price":
                    current_price = self.process_stock_price(dispatcher, company_name)
                    current_price2 =self.process_stock_price(dispatcher, company_name2)
                    if current_price is not None and current_price2 is not None:
                        if current_price > current_price2:
                            dispatcher.utter_message(text=f"The current stock price of {company_name} (${current_price:.2f}) is higher than {company_name2} (${current_price2:.2f}).")
                        elif current_price < current_price2:
                            dispatcher.utter_message(text=f"The current stock price of {company_name} (${current_price:.2f}) is lower than {company_name2} (${current_price2:.2f}).")
                        else:
                            dispatcher.utter_message(text=f"The current stock prices of {company_name} and {company_name2} are equal (${current_price:.2f}).")
                    else:
                        dispatcher.utter_message(text="Sorry, couldn't retrieve stock price data for one or both of the companies.")
                # elif info == "market sentiment":
                #     self.process_market_sentiment(dispatcher, company_name)
                #     self.process_market_sentiment(dispatcher, company_name2)
                # elif info == "volatility":
                #     self.process_stock_volatility(dispatcher, company_name)
                #     self.process_stock_volatility(dispatcher, company_name2)
                else:
                    dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")
            else:
                dispatcher.utter_message(text="Sorry, I couldn't understand the comparison metric.")
        
        except Exception as e:
            dispatcher.utter_message(text="An error occurred while processing the comparison request.")

        return []

    def process_stock_price(self, dispatcher: CollectingDispatcher, company_name: str):
        ticker_mapping = get_ticker_mapping()
        if company_name in ticker_mapping:
            stock_ticker = ticker_mapping[company_name]
            stock_data = yf.Ticker(stock_ticker)
            if len(stock_data.history(period='1d')) > 0:
                current_price = stock_data.history(period='1d')['Close'].iloc[0]
                return current_price
                # dispatcher.utter_message(text=f"The current stock price of {company_name} is ${current_price:.2f}")
            else:
                dispatcher.utter_message(text=f"No data found for the company {company_name}. Please enter a valid company name .")
        else:
            dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        pass

    # def process_market_sentiment(self, dispatcher: CollectingDispatcher, company_name: str):
    #     # Implement the logic to get market sentiment using ActionGetMarketSentiment
    #     pass
    
    # def process_stock_volatility(self, dispatcher: CollectingDispatcher, company_name: str):
    #     # Implement the logic to get stock volatility using ActionGetStockVolatility
    #     pass
