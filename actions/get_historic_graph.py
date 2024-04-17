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
            # entities = tracker.latest_message.get('entities', [])
            # print("Entities extracted:", entities)  # Debug statement
            company_name = next(tracker.get_latest_entity_values("stock_name"), None)
            if company_name:
                company_name = company_name.lower()
            else:
                company_name = tracker.get_slot("stock_name").lower()
            info = next(tracker.get_latest_entity_values("info"), None).lower()
            print("Company name extracted:", company_name)  # Debug statement
            print(info)
            self.check_info_type(dispatcher, company_name, info)
        
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message(text="Sorry, I encountered an error while processing your request.")

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
            info = stock_data.info
            currency = info['currency']
            plt.plot(df.index, df['Close'])
            plt.xlabel('Date')
            plt.ylabel(f'Closing Price in {currency}')
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
            info = stock_data.info
            currency = info['currency']
            plt.plot(revenue_data.index, revenue_data.values)
            plt.xlabel('Date')
            plt.ylabel(f'Revenue in {currency}')
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

    def process_stock_rps_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        revenue_per_share_data = stock_data.history(period="1y").get('revenuePerShare')
        if revenue_per_share_data is not None:
            plt.plot(revenue_per_share_data.index, revenue_per_share_data.values)
            plt.xlabel('Date')
            plt.ylabel('Revenue Per Share')
            plt.title(f'Revenue Per Share Trend for {company_name}')
            plt.grid(True)
            revenue_per_share_plot_file = 'static/images/stock_revenue_per_share.png'
            plt.savefig(revenue_per_share_plot_file)
            plt.close()
            dispatcher.utter_message(image=revenue_per_share_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve Revenue Per Share data.")

    def process_stock_roa_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        return_on_assets_data = stock_data.history(period="1y").get('returnOnAssets')
        if return_on_assets_data is not None:
            plt.plot(return_on_assets_data.index, return_on_assets_data.values)
            plt.xlabel('Date')
            plt.ylabel('Return on Assets')
            plt.title(f'Return on Assets Trend for {company_name}')
            plt.grid(True)
            return_on_assets_plot_file = 'static/images/stock_return_on_assets.png'
            plt.savefig(return_on_assets_plot_file)
            plt.close()
            dispatcher.utter_message(image=return_on_assets_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve Return on Assets data.")

    def process_stock_eg_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        earnings_growth_data = stock_data.history(period="1y").get('earningsGrowth')
        if earnings_growth_data is not None:
            plt.plot(earnings_growth_data.index, earnings_growth_data.values)
            plt.xlabel('Date')
            plt.ylabel('Earnings Growth')
            plt.title(f'Earnings Growth Trend for {company_name}')
            plt.grid(True)
            earnings_growth_plot_file = 'static/images/stock_earnings_growth.png'
            plt.savefig(earnings_growth_plot_file)
            plt.close()
            dispatcher.utter_message(image=earnings_growth_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve Earnings Growth data.")

    def process_stock_rg_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        revenue_growth_data = stock_data.history(period="1y").get('revenueGrowth')
        if revenue_growth_data is not None:
            plt.plot(revenue_growth_data.index, revenue_growth_data.values)
            plt.xlabel('Date')
            plt.ylabel('Revenue Growth')
            plt.title(f'Revenue Growth Trend for {company_name}')
            plt.grid(True)
            revenue_growth_plot_file = 'static/images/stock_revenue_growth.png'
            plt.savefig(revenue_growth_plot_file)
            plt.close()
            dispatcher.utter_message(image=revenue_growth_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve Revenue Growth data.")

    def process_stock_gm_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        gross_margins_data = stock_data.history(period="1y").get('grossMargins')
        if gross_margins_data is not None:
            plt.plot(gross_margins_data.index, gross_margins_data.values)
            plt.xlabel('Date')
            plt.ylabel('Gross Margins')
            plt.title(f'Gross Margins Trend for {company_name}')
            plt.grid(True)
            gross_margins_plot_file = 'static/images/stock_gross_margins.png'
            plt.savefig(gross_margins_plot_file)
            plt.close()
            dispatcher.utter_message(image=gross_margins_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve Gross Margins data.")

    def process_stock_em_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        ebitda_margins_data = stock_data.history(period="1y").get('ebitdaMargins')
        if ebitda_margins_data is not None:
            plt.plot(ebitda_margins_data.index, ebitda_margins_data.values)
            plt.xlabel('Date')
            plt.ylabel('EBITDA Margins')
            plt.title(f'EBITDA Margins Trend for {company_name}')
            plt.grid(True)
            ebitda_margins_plot_file = 'static/images/stock_ebitda_margins.png'
            plt.savefig(ebitda_margins_plot_file)
            plt.close()
            dispatcher.utter_message(image=ebitda_margins_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve EBITDA Margins data.")

    def process_stock_om_graph(self, dispatcher: CollectingDispatcher, company_name: str):
        stock_ticker = get_ticker(company_name)
        stock_data = yf.Ticker(stock_ticker)
        operating_margins_data = stock_data.history(period="1y").get('operatingMargins')
        if operating_margins_data is not None:
            plt.plot(operating_margins_data.index, operating_margins_data.values)
            plt.xlabel('Date')
            plt.ylabel('Operating Margins')
            plt.title(f'Operating Margins Trend for {company_name}')
            plt.grid(True)
            operating_margins_plot_file = 'static/images/stock_operating_margins.png'
            plt.savefig(operating_margins_plot_file)
            plt.close()
            dispatcher.utter_message(image=operating_margins_plot_file)
        else:
            dispatcher.utter_message(text="Unable to retrieve Operating Margins data.")
