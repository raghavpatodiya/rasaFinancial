from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yfinance as yf
from actions.ticker_mapping import get_ticker
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
# class ActionGetGeneralInfo(Action):
#     def name(self) -> Text:
#         return "get_general_info"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         try:
#             company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
#             print("Company name extracted:", company_name)  # Debug statement

#             self.process_info(dispatcher, company_name)

#         except Exception as e:
#             company_name = tracker.get_slot("stock_name").lower()
#             print("Company name extracted:", company_name)  # Debug statement

#             self.process_info(dispatcher, company_name)

#         return []

#     def process_info(self, dispatcher: CollectingDispatcher, company_name: str):
#         stock_ticker = get_ticker(company_name)
#         stock_info = yf.Ticker(stock_ticker)
#         info = stock_info.info
#         info_message = f"Here are some important details about {company_name}:\n\n"
#         info_message += f"Website: {info['website']}\n"
#         info_message += f"Industry: {info['industry']}\n"
#         info_message += f"Sector: {info['sector']}\n"
#         info_message += f"Description: {info['longBusinessSummary']}\n"
#         info_message += f"Number of Employees: {info['fullTimeEmployees']}\n"
#         info_message += f"Leadership Team:\n"
#         for officer in info['companyOfficers']:
#             info_message += f"- {officer['name']}, {officer['title']}\n"
#         info_message += f"Previous Close: {info['previousClose']}\n"
#         info_message += f"Open: {info['open']}\n"
#         info_message += f"Day Low: {info['dayLow']}\n"
#         info_message += f"Day High: {info['dayHigh']}\n"
#         info_message += f"Volume: {info['volume']}\n"
        
#         dispatcher.utter_message(text=info_message)

class ActionGetSpecificInfo(Action):
    def name(self) -> Text:
        return "get_specific_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print("Entities extracted:", entities)  # Debug statement
            
            # Extracting entity values from user message
            company_name = next(tracker.get_latest_entity_values("stock_name"), None).lower()
            info_type = next(tracker.get_latest_entity_values("info"), None).lower()
            print("Company name extracted:", company_name)  # Debug statement
            print("Info type extracted:", info_type)  # Debug statement
            self.process_info(dispatcher, company_name, info_type)

        except Exception as e:
            company_name = tracker.get_slot("stock_name").lower()
            print("Company name extracted:", company_name)  # Debug statement
            info_type = next(tracker.get_latest_entity_values("info"), None)

            self.process_info(dispatcher, company_name, info_type)

        return []
    
    def format(self, amount: str) -> str:
        if amount != 'N/A':
            amount_numeric = float(amount)
            if amount_numeric >= 1e12:
                # Convert to trillion
                formatted = f"{amount_numeric / 1e12:.2f} trillion"
            elif amount_numeric >= 1e9:
                # Convert to billion
                formatted = f"{amount_numeric / 1e9:.2f} billion"
            elif amount_numeric >= 1e6:
                # Convert to million
                formatted = f"{amount_numeric / 1e6:.2f} million"
            else:
                # Leave as is
                formatted = f"{amount_numeric:.2f}"
        else:
            formatted = 'N/A'
        return formatted

    def process_info(self, dispatcher: CollectingDispatcher, company_name: str, info_type: str):
        stock_ticker = get_ticker(company_name)
        stock_info = yf.Ticker(stock_ticker)
        info = stock_info.info
        
        # Retrieving specific information requested by the user
        if info_type in ["number of employee", "number of employees", "total employees", "total employee", "full time employee", "full time employees", "full-time employees"]:
            requested_info = info['fullTimeEmployees']
            dispatcher.utter_message(text=f"The number of employees at {company_name} is: {requested_info}")
        
        elif  info_type in ["city", "country", "location"]:
            requested_info=info['city']+', '+info['country']
            dispatcher.utter_message(text=f"The head-office of {company_name} is at: {requested_info}")
        
        elif info_type in ["website", "url", "link"]:
            requested_info = info['website']
            # html_page = urlopen(requested_info)
            # soup = BeautifulSoup(html_page, 'html.parser')
            # for link in soup.findAll('a'):print(link.get('href'))
            dispatcher.utter_message(text=f"The website of {company_name} is: {requested_info}")
        
        elif info_type in ["industry"]:
            requested_info = info['industry']
            dispatcher.utter_message(text=f"The industry type of {company_name} is: {requested_info}")
        
        elif info_type in ["sector"]:
            requested_info = info['sector']
            dispatcher.utter_message(text=f"The sector type of {company_name} is: {requested_info}")
        
        elif info_type in ["description", "summary", "long summary", "business summary"]:
            requested_info = info['longBusinessSummary']
            dispatcher.utter_message(text=f"The summary of {company_name}: {requested_info}")
        
        elif info_type in ["leadership team", "leadership", "team", "officers"]:
            requested_info = ""  # Initialize requested_info
            for officer in info['companyOfficers']:
                requested_info += f"- {officer['name']}, {officer['title']}\n"
            dispatcher.utter_message(text=f"The leadership team of {company_name}:\n{requested_info}")
        
        elif info_type in ["market cap", "market capitalization", "capital"]:
            requested_info = info['marketCap']
            dispatcher.utter_message(text=f"The market capitalization of {company_name} is: {requested_info}")

        elif info_type in ["previous close"]:
            requested_info = info['previousClose']
            dispatcher.utter_message(text=f"The previous close price of {company_name} was: {requested_info}")

        elif info_type in ["open", "day open"]:
            requested_info = info['open']
            dispatcher.utter_message(text=f"The opening price of {company_name} today was: {requested_info}")

        elif info_type in ["day low"]:
            requested_info = info['dayLow']
            dispatcher.utter_message(text=f"The lowest price of {company_name} today was: {requested_info}")

        elif info_type in ["day high"]:
            requested_info = info['dayHigh']
            dispatcher.utter_message(text=f"The highest price of {company_name} today was: {requested_info}")
        elif info_type in ["audit risk"]:
            requested_info = info['auditRisk']
            dispatcher.utter_message(text=f"The audit risk of {company_name} is: {requested_info}")

        elif info_type in ["board risk"]:
            requested_info = info['boardRisk']
            dispatcher.utter_message(text=f"The board risk of {company_name} is: {requested_info}")

        elif info_type in ["compensation risk"]:
            requested_info = info['compensationRisk']
            dispatcher.utter_message(text=f"The compensation risk of {company_name} is: {requested_info}")

        elif info_type in ["shareholder rights risk", "rights risk"]:
            requested_info = info['shareHolderRightsRisk']
            dispatcher.utter_message(text=f"The shareholder rights risk of {company_name} is: {requested_info}")

        elif info_type in ["overall risk"]:
            requested_info = info['overallRisk']
            dispatcher.utter_message(text=f"The overall risk of {company_name} is: {requested_info}")

        elif info_type in ["governance epoch date"]:
            requested_info = info['governanceEpochDate']
            dispatcher.utter_message(text=f"The governance epoch date of {company_name} is: {requested_info}")

        elif info_type in ["compensation as of epoch date"]:
            requested_info = info['compensationAsOfEpochDate']
            dispatcher.utter_message(text=f"The compensation as of epoch date of {company_name} is: {requested_info}")

        elif info_type in ["max age"]:
            requested_info = info['maxAge']
            dispatcher.utter_message(text=f"The max age of {company_name} is: {requested_info}")

        elif info_type in ["price hint"]:
            requested_info = info['priceHint']
            dispatcher.utter_message(text=f"The price hint of {company_name} is: {requested_info}")

        elif info_type in ["regular market previous close"]:
            requested_info = info['regularMarketPreviousClose']
            dispatcher.utter_message(text=f"The regular market previous close price of {company_name} is: {requested_info}")

        elif info_type in ["regular market open"]:
            requested_info = info['regularMarketOpen']
            dispatcher.utter_message(text=f"The regular market opening price of {company_name} is: {requested_info}")

        elif info_type in ["regular market day low"]:
            requested_info = info['regularMarketDayLow']
            dispatcher.utter_message(text=f"The regular market lowest price of {company_name} today is: {requested_info}")

        elif info_type in ["regular market day high"]:
            requested_info = info['regularMarketDayHigh']
            dispatcher.utter_message(text=f"The regular market highest price of {company_name} today is: {requested_info}")

        elif info_type in ["beta"]:
            requested_info = info['beta']
            dispatcher.utter_message(text=f"The beta of {company_name} is: {requested_info}")

        elif info_type in ["trailing PE", "trailing pe", "pe ratio", "p/e ratio"]:
            requested_info = info['trailingPE']
            dispatcher.utter_message(text=f"The trailing PE of {company_name} is: {requested_info}")

        elif info_type in ["forward PE"]:
            requested_info = info['forwardPE']
            dispatcher.utter_message(text=f"The forward PE of {company_name} is: {requested_info}")

        elif info_type in ["volume"]:
            requested_info = info['volume']
            dispatcher.utter_message(text=f"The volume of {company_name} is: {requested_info}")

        elif info_type in ["regular market volume"]:
            requested_info = info['regularMarketVolume']
            dispatcher.utter_message(text=f"The regular market volume of {company_name} is: {requested_info}")

        elif info_type in ["average volume"]:
            requested_info = info['averageVolume']
            dispatcher.utter_message(text=f"The average volume of {company_name} is: {requested_info}")

        elif info_type in ["average volume 10 days"]:
            requested_info = info['averageVolume10days']
            dispatcher.utter_message(text=f"The average volume of {company_name} for the last 10 days is: {requested_info}")

        elif info_type in ["average daily volume 10 days"]:
            requested_info = info['averageDailyVolume10Day']
            dispatcher.utter_message(text=f"The average daily volume of {company_name} for the last 10 days is: {requested_info}")

        elif info_type in ["bid size"]:
            requested_info = info['bidSize']
            dispatcher.utter_message(text=f"The bid size of {company_name} is: {requested_info}")

        elif info_type in ["ask size"]:
            requested_info = info['askSize']
            dispatcher.utter_message(text=f"The ask size of {company_name} is: {requested_info}")

        elif info_type in ["fifty two week low"]:
            requested_info = info['fiftyTwoWeekLow']
            dispatcher.utter_message(text=f"The fifty two week low of {company_name} is: {requested_info}")

        elif info_type in ["fifty two week high"]:
            requested_info = info['fiftyTwoWeekHigh']
            dispatcher.utter_message(text=f"The fifty two week high of {company_name} is: {requested_info}")

        elif info_type in ["price to sales trailing 12 months"]:
            requested_info = info['priceToSalesTrailing12Months']
            dispatcher.utter_message(text=f"The price to sales trailing 12 months of {company_name} is: {requested_info}")

        elif info_type in ["fifty day average"]:
            requested_info = info['fiftyDayAverage']
            dispatcher.utter_message(text=f"The fifty day average of {company_name} is: {requested_info}")

        elif info_type in ["two hundred day average"]:
            requested_info = info['twoHundredDayAverage']
            dispatcher.utter_message(text=f"The two hundred day average of {company_name} is: {requested_info}")

        elif info_type in ["enterprise value"]:
            requested_info = info['enterpriseValue']
            dispatcher.utter_message(text=f"The enterprise value of {company_name} is: {requested_info}")

        elif info_type in ["profit margins"]:
            requested_info = info['profitMargins']
            dispatcher.utter_message(text=f"The profit margins of {company_name} is: {requested_info}")

        elif info_type in ["float shares"]:
            requested_info = info['floatShares']
            dispatcher.utter_message(text=f"The float shares of {company_name} is: {requested_info}")

        elif info_type in ["shares outstanding"]:
            requested_info = info['sharesOutstanding']
            dispatcher.utter_message(text=f"The shares outstanding of {company_name} is: {requested_info}")

        elif info_type in ["shares short"]:
            requested_info = info['sharesShort']
            dispatcher.utter_message(text=f"The shares short of {company_name} is: {requested_info}")

        elif info_type in ["shares short prior month"]:
            requested_info = info['sharesShortPriorMonth']
            dispatcher.utter_message(text=f"The shares short prior month of {company_name} is: {requested_info}")

        elif info_type in ["shares short previous month date"]:
            requested_info = info['sharesShortPreviousMonthDate']
            dispatcher.utter_message(text=f"The shares short previous month date of {company_name} is: {requested_info}")

        elif info_type in ["date short interest"]:
            requested_info = info['dateShortInterest']
            dispatcher.utter_message(text=f"The date short interest of {company_name} is: {requested_info}")

        elif info_type in ["shares percent shares out"]:
            requested_info = info['sharesPercentSharesOut']
            dispatcher.utter_message(text=f"The shares percent shares out of {company_name} is: {requested_info}")

        elif info_type in ["held percent insiders"]:
            requested_info = info['heldPercentInsiders']
            dispatcher.utter_message(text=f"The held percent insiders of {company_name} is: {requested_info}")

        elif info_type in ["held percent institutions"]:
            requested_info = info['heldPercentInstitutions']
            dispatcher.utter_message(text=f"The held percent institutions of {company_name} is: {requested_info}")

        elif info_type in ["short ratio"]:
            requested_info = info['shortRatio']
            dispatcher.utter_message(text=f"The short ratio of {company_name} is: {requested_info}")

        elif info_type in ["implied shares outstanding"]:
            requested_info = info['impliedSharesOutstanding']
            dispatcher.utter_message(text=f"The implied shares outstanding of {company_name} is: {requested_info}")

        elif info_type in ["book value"]:
            requested_info = info['bookValue']
            dispatcher.utter_message(text=f"The book value of {company_name} is: {requested_info}")

        elif info_type in ["price to book"]:
            requested_info = info['priceToBook']
            dispatcher.utter_message(text=f"The price to book of {company_name} is: {requested_info}")

        elif info_type in ["last fiscal year end"]:
            requested_info = info['lastFiscalYearEnd']
            dispatcher.utter_message(text=f"The last fiscal year end of {company_name} is: {requested_info}")

        elif info_type in ["next fiscal year end"]:
            requested_info = info['nextFiscalYearEnd']
            dispatcher.utter_message(text=f"The next fiscal year end of {company_name} is: {requested_info}")

        elif info_type in ["most recent quarter"]:
            requested_info = info['mostRecentQuarter']
            dispatcher.utter_message(text=f"The most recent quarter of {company_name} is: {requested_info}")

        elif info_type in ["earnings quarterly growth"]:
            requested_info = info['earningsQuarterlyGrowth']
            dispatcher.utter_message(text=f"The earnings quarterly growth of {company_name} is: {requested_info}")

        elif info_type in ["net income to common"]:
            requested_info = info['netIncomeToCommon']
            dispatcher.utter_message(text=f"The net income to common of {company_name} is: {requested_info}")

        elif info_type in ["trailing eps", "earning per share", "earnings per share"]:
            requested_info = info['trailingEps']
            dispatcher.utter_message(text=f"The trailing EPS of {company_name} is: {requested_info}")

        elif info_type in ["forward eps"]:
            requested_info = info['forwardEps']
            dispatcher.utter_message(text=f"The forward EPS of {company_name} is: {requested_info}")

        elif info_type in ["peg ratio"]:
            requested_info = info['pegRatio']
            dispatcher.utter_message(text=f"The PEG ratio of {company_name} is: {requested_info}")

        elif info_type in ["last split factor"]:
            requested_info = info['lastSplitFactor']
            dispatcher.utter_message(text=f"The last split factor of {company_name} is: {requested_info}")

        elif info_type in ["last split date"]:
            requested_info = info['lastSplitDate']
            dispatcher.utter_message(text=f"The last split date of {company_name} is: {requested_info}")

        elif info_type in ["enterprise to revenue"]:
            requested_info = info['enterpriseToRevenue']
            dispatcher.utter_message(text=f"The enterprise to revenue of {company_name} is: {requested_info}")

        elif info_type in ["enterprise to ebitda"]:
            requested_info = info['enterpriseToEbitda']
            dispatcher.utter_message(text=f"The enterprise to EBITDA of {company_name} is: {requested_info}")

        elif info_type in ["52 week change"]:
            requested_info = info['52WeekChange']
            dispatcher.utter_message(text=f"The 52-week change of {company_name} is: {requested_info}")

        elif info_type in ["S&P 52 week change"]:
            requested_info = info['SandP52WeekChange']
            dispatcher.utter_message(text=f"The S&P 52-week change of {company_name} is: {requested_info}")

        elif info_type in ["exchange"]:
            requested_info = info['exchange']
            dispatcher.utter_message(text=f"The exchange of {company_name} is: {requested_info}")

        elif info_type in ["quote type"]:
            requested_info = info['quoteType']
            dispatcher.utter_message(text=f"The quote type of {company_name} is: {requested_info}")

        elif info_type in ["symbol", "ticker", "ticker symbol"]:
            requested_info = info['symbol']
            dispatcher.utter_message(text=f"The symbol of {company_name} is: {requested_info}")

        elif info_type in ["underlying symbol"]:
            requested_info = info['underlyingSymbol']
            dispatcher.utter_message(text=f"The underlying symbol of {company_name} is: {requested_info}")

        elif info_type in ["short name"]:
            requested_info = info['shortName']
            dispatcher.utter_message(text=f"The short name of {company_name} is: {requested_info}")

        elif info_type in ["long name"]:
            requested_info = info['longName']
            dispatcher.utter_message(text=f"The long name of {company_name} is: {requested_info}")

        elif info_type in ["first trade date epoch utc"]:
            requested_info = info['firstTradeDateEpochUtc']
            dispatcher.utter_message(text=f"The first trade date epoch UTC of {company_name} is: {requested_info}")

        elif info_type in ["time zone full name"]:
            requested_info = info['timeZoneFullName']
            dispatcher.utter_message(text=f"The time zone full name of {company_name} is: {requested_info}")

        elif info_type in ["time zone short name"]:
            requested_info = info['timeZoneShortName']
            dispatcher.utter_message(text=f"The time zone short name of {company_name} is: {requested_info}")

        elif info_type in ["uuid"]:
            requested_info = info['uuid']
            dispatcher.utter_message(text=f"The UUID of {company_name} is: {requested_info}")

        elif info_type in ["message board id"]:
            requested_info = info['messageBoardId']
            dispatcher.utter_message(text=f"The message board ID of {company_name} is: {requested_info}")

        elif info_type in ["gmt offset milliseconds"]:
            requested_info = info['gmtOffSetMilliseconds']
            dispatcher.utter_message(text=f"The GMT offset milliseconds of {company_name} is: {requested_info}")

        elif info_type in ["recommendation mean"]:
            requested_info = info['recommendationMean']
            dispatcher.utter_message(text=f"The recommendation mean of {company_name} is: {requested_info}")

        elif info_type in ["recommendation key"]:
            requested_info = info['recommendationKey']
            dispatcher.utter_message(text=f"The recommendation key of {company_name} is: {requested_info}")

        elif info_type in ["number of analyst opinions"]:
            requested_info = info['numberOfAnalystOpinions']
            dispatcher.utter_message(text=f"The number of analyst opinions for {company_name} is: {requested_info}")

        elif info_type in ["total cash"]:
            requested_info = info['totalCash']
            dispatcher.utter_message(text=f"The total cash of {company_name} is: {requested_info}")

        elif info_type in ["total cash per share"]:
            requested_info = info['totalCashPerShare']
            dispatcher.utter_message(text=f"The total cash per share of {company_name} is: {requested_info}")

        elif info_type in ["ebitda"]:
            requested_info = info['ebitda']
            dispatcher.utter_message(text=f"The EBITDA of {company_name} is: {requested_info}")

        elif info_type in ["total debt"]:
            requested_info = info['totalDebt']
            dispatcher.utter_message(text=f"The total debt of {company_name} is: {requested_info}")

        elif info_type in ["quick ratio"]:
            requested_info = info['quickRatio']
            dispatcher.utter_message(text=f"The quick ratio of {company_name} is: {requested_info}")

        elif info_type in ["current ratio"]:
            requested_info = info['currentRatio']
            dispatcher.utter_message(text=f"The current ratio of {company_name} is: {requested_info}")

        elif info_type in ["total revenue"]:
            requested_info = info['totalRevenue']
            dispatcher.utter_message(text=f"The total revenue of {company_name} is: {requested_info}")

        elif info_type in ["debt to equity"]:
            requested_info = info['debtToEquity']
            dispatcher.utter_message(text=f"The debt to equity ratio of {company_name} is: {requested_info}")

        elif info_type in ["revenue per share"]:
            requested_info = info['revenuePerShare']
            dispatcher.utter_message(text=f"The revenue per share of {company_name} is: {requested_info}")

        elif info_type in ["return on assets"]:
            requested_info = info['returnOnAssets']
            dispatcher.utter_message(text=f"The return on assets of {company_name} is: {requested_info}")

        elif info_type in ["return on equity"]:
            requested_info = info['returnOnEquity']
            dispatcher.utter_message(text=f"The return on equity of {company_name} is: {requested_info}")

        elif info_type in ["free cashflow"]:
            requested_info = info['freeCashflow']
            dispatcher.utter_message(text=f"The free cashflow of {company_name} is: {requested_info}")

        elif info_type in ["operating cashflow"]:
            requested_info = info['operatingCashflow']
            dispatcher.utter_message(text=f"The operating cashflow of {company_name} is: {requested_info}")

        elif info_type in ["earnings growth"]:
            requested_info = info['earningsGrowth']
            dispatcher.utter_message(text=f"The earnings growth of {company_name} is: {requested_info}")

        elif info_type in ["revenue growth"]:
            requested_info = info['revenueGrowth']
            dispatcher.utter_message(text=f"The revenue growth of {company_name} is: {requested_info}")

        elif info_type in ["gross margins"]:
            requested_info = info['grossMargins']
            dispatcher.utter_message(text=f"The gross margins of {company_name} is: {requested_info}")

        elif info_type in ["ebitda margins"]:
            requested_info = info['ebitdaMargins']
            dispatcher.utter_message(text=f"The EBITDA margins of {company_name} is: {requested_info}")

        elif info_type in ["operating margins"]:
            requested_info = info['operatingMargins']
            dispatcher.utter_message(text=f"The operating margins of {company_name} is: {requested_info}")

        elif info_type in ["financial currency", "currency"]:
            requested_info = info['financialCurrency']
            dispatcher.utter_message(text=f"The financial currency of {company_name} is: {requested_info}")

        elif info_type in ["trailing peg ratio"]:
            requested_info = info['trailingPegRatio']
            dispatcher.utter_message(text=f"The trailing PEG ratio of {company_name} is: {requested_info}")

        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find the requested information for {company_name}.")
