from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yfinance as yf
from actions.ticker_mapping import get_ticker
import requests
class ActionGetGeneralInfo(Action):
    def name(self) -> Text:
        return "get_general_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            print("Company name extracted:", company_name)  # Debug statement

            self.process_info(dispatcher, company_name)

        except Exception as e:
            company_name = tracker.get_slot("stock_name").lower()
            print("Company name extracted:", company_name)  # Debug statement

            self.process_info(dispatcher, company_name)

        return []

    def process_info(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_info = yf.Ticker(stock_ticker)
        info = stock_info.info
        print(info)
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

class ActionGetSpecificInfo(Action):
    def name(self) -> Text:
        return "get_specific_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            
            # Extracting entity values from user message
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            info_type = next(tracker.get_latest_entity_values("info"), None)
            print("Company name extracted:", company_name)  # Debug statement
            print("Info type extracted:", info_type)  # Debug statement
            self.process_info(dispatcher, company_name, info_type)

        except Exception as e:
            company_name = tracker.get_slot("stock_name").lower()
            print("Company name extracted:", company_name)  # Debug statement
            info_type = next(tracker.get_latest_entity_values("info"), None)

            self.process_info(dispatcher, company_name, info_type)

        return []

    def process_info(self, dispatcher: CollectingDispatcher, company_name: str, info_type: str):
        stock_ticker = get_ticker(company_name)
        stock_info = yf.Ticker(stock_ticker)
        info = stock_info.info
        
        # Retrieving specific information requested by the user
        if info_type in info:
            requested_info = info[info_type]
            dispatcher.utter_message(text=f"The {info_type} of {company_name} is: {requested_info}")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find the requested information for {company_name}.")
