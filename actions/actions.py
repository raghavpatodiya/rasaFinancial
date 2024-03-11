from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yfinance as yf
from actions.ticker_mapping import get_ticker_mapping

class ActionGetStockPrice(Action):
    def name(self) -> Text:
        return "get_latest_stock_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            print("Company name extracted:", company_name)  # Debug statement

            ticker_mapping = get_ticker_mapping()
            if company_name.lower() in ticker_mapping:
                stock_ticker = ticker_mapping[company_name.lower()]
                stock_data = yf.Ticker(stock_ticker)
                if len(stock_data.history(period='1d')) > 0:
                    current_price = stock_data.history(period='1d')['Close'][0]
                    dispatcher.utter_message(text=f"The current stock price of {company_name} is ${current_price:.2f}")
                else:
                    dispatcher.utter_message(text=f"No data found for the company {company_name}. Please enter a valid company name .")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        
        except Exception as e:
            print(f"An error occurred while fetching stock price: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")

        return []

class ActionGetOlderStockPrice(Action):
    def name(self)->Text:
        return "get_older_stock_price"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            time_period = next(tracker.get_latest_entity_values("time_period"), None)
            print("Company name extracted:", company_name)  # Debug statement
            print("Time period extracted:", time_period)  # Debug statement

            ticker_mapping = get_ticker_mapping()
            if company_name.lower() in ticker_mapping:
                stock_ticker = ticker_mapping[company_name.lower()]
                stock_data = yf.Ticker(stock_ticker)
                if time_period in ["one year", "1 year"]:
                    stock_history = stock_data.history(period='1y')
                elif time_period in ["six months", "6 months"]:
                    stock_history = stock_data.history(period='6mo')
                elif time_period in ["two months", "2 months"]:
                    stock_history = stock_data.history(period='2mo')
                elif time_period in ["one month", "1 month"]:
                    stock_history = stock_data.history(period='1mo')
                elif time_period in ["one week", "1 week"]:
                    stock_history = stock_data.history(period='1wk')
                elif time_period in ["three days", "3 days"]:
                    stock_history = stock_data.history(period='3d')
                else:
                    dispatcher.utter_message(text="Unsupported time period. Please try again.")
                    return []

                if len(stock_history) > 0:
                    current_price = stock_history['Close'].iloc[-1]  # Get the latest close price
                    dispatcher.utter_message(text=f"The {time_period} stock price of {company_name} is ${current_price:.2f}")
                else:
                    dispatcher.utter_message(text=f"No data found for the company {company_name}. Please enter a valid company name.")
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        except Exception as e:
            print(f"An error occurred while fetching stock price: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock price. Please try again later.")

        return []
    
class ActionGetStockInfo(Action):
    def name(self) -> Text:
        return "get_stock_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            print("Company name extracted:", company_name)  # Debug statement

            ticker_mapping = get_ticker_mapping()
            if company_name.lower() in ticker_mapping:
                stock_ticker = ticker_mapping[company_name.lower()]
                stock_info = yf.Ticker(stock_ticker)
                info = stock_info.info
                print(info)
                # Constructing the message with the 10 important points
                info_message = f"Here are some important details about {company_name}:\n\n"
                info_message += f"Website: {info['website']}\n"
                info_message += f"Industry: {info['industry']}\n"
                info_message += f"Sector: {info['sector']}\n"
                info_message += f"Description: {info['longBusinessSummary']}\n"
                info_message += f"Number of Employees: {info['fullTimeEmployees']}\n"
                info_message += f"Leadership Team:\n"
                for officer in info['companyOfficers']:
                    info_message += f"- {officer['name']}, {officer['title']}\n"
                info_message += f"Previous Close: {info['previousClose']}\n"
                info_message += f"Open: {info['open']}\n"
                info_message += f"Day Low: {info['dayLow']}\n"
                info_message += f"Day High: {info['dayHigh']}\n"
                info_message += f"Volume: {info['volume']}\n"
                
                dispatcher.utter_message(text=info_message)
            else:
                dispatcher.utter_message(text="I couldn't identify the stock name. Please provide a valid stock name.")
        except Exception as e:
            print(f"An error occurred while fetching stock information: {e}")
            dispatcher.utter_message(text="An error occurred while fetching stock information. Please try again later.")

        return []
