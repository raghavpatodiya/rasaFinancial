# Add the following imports at the top of your script
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.ticker_mapping import get_ticker
from typing import Any, Text, Dict, List
import yfinance as yf
import matplotlib.pyplot as plt

# Add the new action class here
class ActionGetStockTrendGraph(Action):
    def name(self) -> Text:
        return "get_graph"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            print("Company name extracted:", company_name)  # Debug statement
            self.process_stock_trend_graph(dispatcher, company_name)
        
        except Exception as e:
            # Extract stock_name from the slot
            company_name = tracker.get_slot("stock_name").lower()
            print("Company name extracted from slot:", company_name)  # Debug statement
            self.process_stock_trend_graph(dispatcher, company_name)

        return []

    def process_stock_trend_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        df = stock_data.history(period="1wk")  # Fetch historical data for all available dates
        if not df.empty:
            plt.plot(df.index, df['Close'])
            plt.xlabel('Date')
            plt.ylabel('Closing Price')
            plt.title(f'Stock Trend for {company_name}')
            plt.xticks(rotation=45)
            plt.grid(True)
            # Save the plot as a file
            graph_file = 'static/images/stock_graph.png'  # Save the graph in the static folder
            plt.savefig(graph_file)
            plt.close()

            # Send the graph file as a response
            dispatcher.utter_message(image=graph_file)
        else:
            dispatcher.utter_message(text="Unable to analyze trend. No historical data available.")