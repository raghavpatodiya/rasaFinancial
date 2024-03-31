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
            info = next(tracker.get_latest_entity_values("info"), None).lower()
            print("Company name extracted:", company_name)  # Debug statement
            print(info)
            self.check_info_type(dispatcher, company_name, info)
        
        except Exception as e:
            # Extract stock_name from the slot
            company_name = tracker.get_slot("stock_name").lower()
            info = next(tracker.get_latest_entity_values("info"), None).lower()
            print("Company name extracted from slot:", company_name)  # Debug statement
            print(info)
            self.check_info_type(dispatcher, company_name, info)

        return []
    
    def check_info_type(self, dispatcher: CollectingDispatcher, company_name: str, info: str):
        if info in ["trend", "price", "stock price"]:
            self.process_stock_trend_graph(dispatcher, company_name)
        elif info in ["roe", "return on equity"]:
            self.process_stock_roe_graph(dispatcher, company_name)
        elif info == "revenue":
            self.process_stock_revenue_graph(dispatcher, company_name)
        elif info in ["volume", "vol"]:
            self.process_stock_volume_graph(dispatcher, company_name)
        else:
            dispatcher.utter_message(text=f"Sorry, {info.replace('_', ' ')} information is not supported.")
    
    def process_stock_trend_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        df = stock_data.history(period="1wk")  # Fetch historical data for all available dates
        if not df.empty:
            plt.plot(df.index, df['Close'])
            plt.xlabel('Date')
            plt.ylabel('Closing Price in $')
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

    def process_stock_roe_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        roe_data = stock_data.history(period="1y").get('returnOnEquity')
        if roe_data is not None:
            plt.plot(roe_data.index, roe_data.values)
            plt.xlabel('Date')
            plt.ylabel('ROE')
            plt.title(f'ROE Trend for {company_name}')
            plt.grid(True)
            roe_plot_file = 'static/images/stock_graph.png'
            plt.savefig(roe_plot_file)
            plt.close()
            dispatcher.utter_message(image=roe_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve ROE data.")
    
    def process_stock_revenue_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        revenue_data = stock_data.history(period="1y").get('revenue')
        if revenue_data is not None:
            plt.plot(revenue_data.index, revenue_data.values)
            plt.xlabel('Date')
            plt.ylabel('Revenue')
            plt.title(f'Revenue Trend for {company_name}')
            plt.grid(True)
            revenue_plot_file = 'static/images/stock_graph.png'
            plt.savefig(revenue_plot_file)
            plt.close()
            dispatcher.utter_message(image=revenue_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve revenue data.")

    def process_stock_volume_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        volume_data = stock_data.history(period="1y").get('volume')
        if volume_data is not None:
            plt.plot(volume_data.index, volume_data.values)
            plt.xlabel('Date')
            plt.ylabel('Volume')
            plt.title(f'Volume Trend for {company_name}')
            plt.grid(True)
            volume_plot_file = 'static/images/stock_graph.png'
            plt.savefig(volume_plot_file)
            plt.close()
            dispatcher.utter_message(image=volume_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve volume data.")