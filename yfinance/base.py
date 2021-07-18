#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Yahoo! Finance market data downloader (+fix for Pandas Datareader)
# https://github.com/ranaroussi/yfinance
#
# Copyright 2017-2019 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function


import time as _time
import datetime as _datetime
from numpy.lib.function_base import iterable
import requests as _requests
import pandas as _pd
import numpy as _np

try:
    from urllib.parse import quote as urlencode
except ImportError:
    from urllib import quote as urlencode

from . import utils

# import json as _json
# import re as _re
# import sys as _sys

from . import shared

_pd.set_option('display.max_rows', None)
_pd.set_option('display.max_columns', None)

class TickerBase():
    def __init__(self, ticker, session=None):
        self.ticker = ticker.upper()
        self.session = session or _requests
        self._history = None
        self._base_url = 'https://query2.finance.yahoo.com'
        self._scrape_url = 'https://finance.yahoo.com/quote'

        self._fundamentals = False
        self._info = None
        self._sustainability = None
        self._recommendations = None
        self._analyst_trend_details = None
        self._analyst_price_target = None
        self._rev_est = None
        self._eps_est = None
        
        self._major_holders = None
        self._institutional_holders = None
        self._mutualfund_holders = None
        self._isin = None

        self._calendar = None
        self._expirations = {}

        self._income_statement = None
        self._balance_sheet = None
        self._cash_flow_statement = None
        self._earnings = {
            "yearly": utils.empty_df(),
            "quarterly": utils.empty_df()}
        self._quarterly_income_statement = {
            # "yearly": utils.empty_df(),
            "quarterly": utils.empty_df()}
        self._quarterly_balance_sheet = {
            # "yearly": utils.empty_df(),
            "quarterly": utils.empty_df()}
        self._quarterly_cash_flow = {
            # "yearly": utils.empty_df(),
            "quarterly": utils.empty_df()}

    def history(self, period="1mo", interval="1d",
                start=None, end=None, prepost=False, actions=True,
                auto_adjust=True, back_adjust=False,
                proxy=None, rounding=False, tz=None, **kwargs):
        """
        :Parameters:
            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
            prepost : bool
                Include Pre and Post market data in results?
                Default is False
            auto_adjust: bool
                Adjust all OHLC automatically? Default is True
            back_adjust: bool
                Back-adjusted data to mimic true historical prices
            proxy: str
                Optional. Proxy server URL scheme. Default is None
            rounding: bool
                Round values to 2 decimal places?
                Optional. Default is False = precision suggested by Yahoo!
            tz: str
                Optional timezone locale for dates.
                (default data is returned as non-localized dates)
            **kwargs: dict
                debug: bool
                    Optional. If passed as False, will suppress
                    error message printing to console.
        """

        if start or period is None or period.lower() == "max":
            if start is None:
                start = -2208988800
            elif isinstance(start, _datetime.datetime):
                start = int(_time.mktime(start.timetuple()))
            else:
                start = int(_time.mktime(
                    _time.strptime(str(start), '%Y-%m-%d')))
            if end is None:
                end = int(_time.time())
            elif isinstance(end, _datetime.datetime):
                end = int(_time.mktime(end.timetuple()))
            else:
                end = int(_time.mktime(_time.strptime(str(end), '%Y-%m-%d')))

            params = {"period1": start, "period2": end}
        else:
            period = period.lower()
            params = {"range": period}

        params["interval"] = interval.lower()
        params["includePrePost"] = prepost
        params["events"] = "div,splits"

        # 1) fix weired bug with Yahoo! - returning 60m for 30m bars
        if params["interval"] == "30m":
            params["interval"] = "15m"

        # setup proxy in requests format
        if proxy is not None:
            if isinstance(proxy, dict) and "https" in proxy:
                proxy = proxy["https"]
            proxy = {"https": proxy}

        # Getting data from json
        url = "{}/v8/finance/chart/{}".format(self._base_url, self.ticker)
        data = self.session.get(
            url=url,
            params=params,
            proxies=proxy,
            headers=utils.user_agent_headers
        )
        if "Will be right back" in data.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n"
                               "Our engineers are working quickly to resolve "
                               "the issue. Thank you for your patience.")
        data = data.json()

        # Work with errors
        debug_mode = True
        if "debug" in kwargs and isinstance(kwargs["debug"], bool):
            debug_mode = kwargs["debug"]

        err_msg = "No data found for this date range, symbol may be delisted"
        if "chart" in data and data["chart"]["error"]:
            err_msg = data["chart"]["error"]["description"]
            shared._DFS[self.ticker] = utils.empty_df()
            shared._ERRORS[self.ticker] = err_msg
            if "many" not in kwargs and debug_mode:
                print('- %s: %s' % (self.ticker, err_msg))
            return shared._DFS[self.ticker]

        elif "chart" not in data or data["chart"]["result"] is None or \
                not data["chart"]["result"]:
            shared._DFS[self.ticker] = utils.empty_df()
            shared._ERRORS[self.ticker] = err_msg
            if "many" not in kwargs and debug_mode:
                print('- %s: %s' % (self.ticker, err_msg))
            return shared._DFS[self.ticker]

        # parse quotes
        try:
            quotes = utils.parse_quotes(data["chart"]["result"][0], tz)
        except Exception:
            shared._DFS[self.ticker] = utils.empty_df()
            shared._ERRORS[self.ticker] = err_msg
            if "many" not in kwargs and debug_mode:
                print('- %s: %s' % (self.ticker, err_msg))
            return shared._DFS[self.ticker]

        # 2) fix weired bug with Yahoo! - returning 60m for 30m bars
        if interval.lower() == "30m":
            quotes2 = quotes.resample('30T')
            quotes = _pd.DataFrame(index=quotes2.last().index, data={
                'Open': quotes2['Open'].first(),
                'High': quotes2['High'].max(),
                'Low': quotes2['Low'].min(),
                'Close': quotes2['Close'].last(),
                'Adj Close': quotes2['Adj Close'].last(),
                'Volume': quotes2['Volume'].sum()
            })
            try:
                quotes['Dividends'] = quotes2['Dividends'].max()
            except Exception:
                pass
            try:
                quotes['Stock Splits'] = quotes2['Dividends'].max()
            except Exception:
                pass

        try:
            if auto_adjust:
                quotes = utils.auto_adjust(quotes)
            elif back_adjust:
                quotes = utils.back_adjust(quotes)
        except Exception as e:
            if auto_adjust:
                err_msg = "auto_adjust failed with %s" % e
            else:
                err_msg = "back_adjust failed with %s" % e
            shared._DFS[self.ticker] = utils.empty_df()
            shared._ERRORS[self.ticker] = err_msg
            if "many" not in kwargs and debug_mode:
                print('- %s: %s' % (self.ticker, err_msg))

        if rounding:
            quotes = _np.round(quotes, data[
                "chart"]["result"][0]["meta"]["priceHint"])
        quotes['Volume'] = quotes['Volume'].fillna(0).astype(_np.int64)

        quotes.dropna(inplace=True)

        # actions
        dividends, splits = utils.parse_actions(data["chart"]["result"][0], tz)

        # combine
        df = _pd.concat([quotes, dividends, splits], axis=1, sort=True)
        df["Dividends"].fillna(0, inplace=True)
        df["Stock Splits"].fillna(0, inplace=True)

        # index eod/intraday
        df.index = df.index.tz_localize("UTC").tz_convert(
            data["chart"]["result"][0]["meta"]["exchangeTimezoneName"])

        if params["interval"][-1] == "m":
            df.index.name = "Datetime"
        elif params["interval"] == "1h":
            pass
        else:
            df.index = _pd.to_datetime(df.index.date)
            if tz is not None:
                df.index = df.index.tz_localize(tz)
            df.index.name = "Date"

        # duplicates and missing rows cleanup
        df.dropna(how='all', inplace=True)
        df.drop_duplicates(inplace=True)
        df = df.groupby(df.index).last()

        self._history = df.copy()

        if not actions:
            df.drop(columns=["Dividends", "Stock Splits"], inplace=True)
        return df

    def _get_fundamentals(self, kind=None, proxy=None):
        def cleanup(data):
            '''
            The cleanup function is used for parsing yahoo finance json financial statement data into a pandas dataframe format.
            '''
            df = _pd.DataFrame(data).drop(columns=['maxAge'])
            for col in df.columns:
                df[col] = _np.where(
                    df[col].astype(str) == '-', _np.nan, df[col])

            df.set_index('endDate', inplace=True)
            try:
                df.index = _pd.to_datetime(df.index, unit='s')
            except ValueError:
                df.index = _pd.to_datetime(df.index)
            df = df.T
            df.columns.name = ''
            df.index.name = 'Breakdown'

            df.index = utils.camel2title(df.index)
            return df

        #------------------ Setup Proxy in Requests Format ------------------
        if proxy is not None:
            if isinstance(proxy, dict) and "https" in proxy:
                proxy = proxy["https"]
            proxy = {"https": proxy}

        if self._fundamentals:
            return

        ticker_url = "{}/{}".format(self._scrape_url, self.ticker)

        #------------------ Holders ------------------ 
        try:
            resp = utils.get_html(ticker_url + '/holders', proxy, self.session)
            holders = _pd.read_html(resp)
        except Exception as e:
            holders = []

        if len(holders) >= 3:
            self._major_holders = holders[0]
            self._institutional_holders = holders[1]
            self._mutualfund_holders = holders[2]
        elif len(holders) >= 2:
            self._major_holders = holders[0]
            self._institutional_holders = holders[1]
        elif len(holders) >= 1:
            self._major_holders = holders[0]

        #self._major_holders = holders[0]
        #self._institutional_holders = holders[1]

        if self._institutional_holders is not None:
            if 'Date Reported' in self._institutional_holders:
                self._institutional_holders['Date Reported'] = _pd.to_datetime(
                    self._institutional_holders['Date Reported'])
            if '% Out' in self._institutional_holders:
                self._institutional_holders['% Out'] = self._institutional_holders[
                    '% Out'].str.replace('%', '').astype(float)/100

        if self._mutualfund_holders is not None:
            if 'Date Reported' in self._mutualfund_holders:
                self._mutualfund_holders['Date Reported'] = _pd.to_datetime(
                    self._mutualfund_holders['Date Reported'])
            if '% Out' in self._mutualfund_holders:
                self._mutualfund_holders['% Out'] = self._mutualfund_holders[
                    '% Out'].str.replace('%', '').astype(float)/100

        #------------------ Sustainability ------------------
        data = utils.get_json(ticker_url, proxy, self.session)
        d = {}
        try:
            if isinstance(data.get('esgScores'), dict):
                for item in data['esgScores']:
                    if not isinstance(data['esgScores'][item], (dict, list)):
                        d[item] = data['esgScores'][item]

                s = _pd.DataFrame(index=[0], data=d)[-1:].T
                s.columns = ['Value']
                s.index.name = '%.f-%.f' % (
                    s[s.index == 'ratingYear']['Value'].values[0],
                    s[s.index == 'ratingMonth']['Value'].values[0])

                self._sustainability = s[~s.index.isin(
                    ['maxAge', 'ratingYear', 'ratingMonth'])]
        except Exception:
            pass

        #------------------ Info (be nice to python 2) ------------------
        self._info = {}
        try:
            items = ['summaryProfile', 'financialData', 'quoteType',
                     'defaultKeyStatistics', 'assetProfile', 'summaryDetail']
            for item in items:
                if isinstance(data.get(item), dict):
                    self._info.update(data[item])
        except Exception:
            pass

        if not isinstance(data.get('summaryDetail'), dict):
            # For some reason summaryDetail did not give any results. The price dict usually has most of the same info
            self._info.update(data.get('price', {}))

        try:
            # self._info['regularMarketPrice'] = self._info['regularMarketOpen']
            self._info['regularMarketPrice'] = data.get('price', {}).get(
                'regularMarketPrice', self._info.get('regularMarketOpen', None))
        except Exception:
            pass

        self._info['logo_url'] = ""
        try:
            domain = self._info['website'].split(
                '://')[1].split('/')[0].replace('www.', '')
            self._info['logo_url'] = 'https://logo.clearbit.com/%s' % domain
        except Exception:
            pass

        #------------------ Events ------------------
        try:
            cal = _pd.DataFrame(
                data['calendarEvents']['earnings'])
            cal['earningsDate'] = _pd.to_datetime(
                cal['earningsDate'], unit='s')
            self._calendar = cal.T
            self._calendar.index = utils.camel2title(self._calendar.index)
            self._calendar.columns = ['Value']
        except Exception:
            pass

        #------------------ Long Term Analyst Recommendations ------------------
        try:
            rec = _pd.DataFrame(
                data['upgradeDowngradeHistory']['history'])
            rec['earningsDate'] = _pd.to_datetime(
                rec['epochGradeDate'], unit='s')
            rec.set_index('earningsDate', inplace=True)
            rec.index.name = 'Date'
            rec.columns = utils.camel2title(rec.columns)
            self._recommendations = rec[[
                'Firm', 'To Grade', 'From Grade', 'Action']].sort_index()
        except Exception:
            pass
        #------------------ Quarterly Income Statement, Balance Sheet and Cash Flow ------------------
        financials_data = utils.get_json(ticker_url+'/financials', proxy, self.session)
        data = financials_data['context']['dispatcher']['stores']['QuoteSummaryStore']
        # generic patterns
        for key in (
            (self._quarterly_cash_flow, 'cashflowStatement', 'cashflowStatements'),
            (self._quarterly_balance_sheet, 'balanceSheet', 'balanceSheetStatements'),
            (self._quarterly_income_statement, 'incomeStatement', 'incomeStatementHistory')
        ):
            # item = key[1] + 'History'
            # if isinstance(data.get(item), dict):
            #     try:
            #         key[0]['yearly'] = cleanup(data[item][key[2]])
            #     except Exception as e:
            #         pass

            item = key[1]+'HistoryQuarterly'
            if isinstance(data.get(item), dict):
                try:
                    key[0]['quarterly'] = cleanup(data[item][key[2]])
                except Exception as e:
                    pass

        #------------------ Earnings ------------------
        if isinstance(data.get('earnings'), dict):
            try:
                earnings = data['earnings']['financialsChart']
                earnings['financialCurrency'] = 'USD' if 'financialCurrency' not in data['earnings'] else data['earnings']['financialCurrency']
                self._earnings['financialCurrency'] = earnings['financialCurrency']
                df = _pd.DataFrame(earnings['yearly']).set_index('date')
                df.columns = utils.camel2title(df.columns)
                df.index.name = 'Year'
                self._earnings['yearly'] = df

                df = _pd.DataFrame(earnings['quarterly']).set_index('date')
                df.columns = utils.camel2title(df.columns)
                df.index.name = 'Quarter'
                self._earnings['quarterly'] = df
            except Exception as e:
                pass

        #------------------ Income Statement ------------------ 
        try:
            data = financials_data['context']['dispatcher']['stores']['FinancialTemplateStore']   # Grab the financial template store. This  details the order in which the financials should be presented.
            financials_template_ttm_order, financials_template_annual_order, financials_level_detail = utils.build_template(data)
            
            data = financials_data['context']['dispatcher']['stores']['QuoteTimeSeriesStore'] # Grab the raw financial details (this can be later combined with the financial template store detail to correctly order and present the data).
            TTM_dicts, Annual_dicts = utils.retreive_financial_details(data)
        
            TTM = _pd.DataFrame.from_dict(TTM_dicts).set_index("index")
            Annual = _pd.DataFrame.from_dict(Annual_dicts).set_index("index")
            # Combine the raw financial details and the template
            TTM = TTM.reindex(financials_template_ttm_order)
            Annual = Annual.reindex(financials_template_annual_order)
            TTM.columns = ['TTM ' + str(col) for col in TTM.columns] # Add 'TTM' prefix to all column names, so if combined we can tell the difference between actuals and TTM (similar to yahoo finance).
            TTM.index = TTM.index.str.replace(r'trailing', '')
            Annual.index = Annual.index.str.replace(r'annual','')
            _income_statement = Annual.merge(TTM, left_index=True, right_index=True)
            _income_statement.index = utils.camel2title(_income_statement.T)
            _income_statement['level_detail'] = financials_level_detail 
            _income_statement = _income_statement.set_index([_income_statement.index,'level_detail'])
            self._income_statement = _income_statement.dropna(how='all')
        except Exception as e:
            self._income_statement = _pd.DataFrame()
        
        #------------------ Balance Sheet ------------------ 
        try:
            balance_sheet_data = utils.get_json(ticker_url+'/balance-sheet', proxy, self.session)
            data = balance_sheet_data['context']['dispatcher']['stores']['FinancialTemplateStore']
            balance_sheet_template_ttm_order, balance_sheet_template_annual_order, balance_sheet_level_detail = utils.build_template(data)
            
            data = balance_sheet_data['context']['dispatcher']['stores']['QuoteTimeSeriesStore']
            TTM_dicts, Annual_dicts = utils.retreive_financial_details(data)
        
            Annual = _pd.DataFrame.from_dict(Annual_dicts).set_index("index")
            Annual = Annual.reindex(balance_sheet_template_annual_order)
            Annual.index = Annual.index.str.replace(r'annual','')
            Annual.index = utils.camel2title(Annual.T)
            _balance_sheet = Annual
            _balance_sheet['level_detail'] = balance_sheet_level_detail 
            _balance_sheet = _balance_sheet.set_index([_balance_sheet.index,'level_detail'])
            self._balance_sheet = _balance_sheet.dropna(how='all')
        except Exception as e:
            self._balance_sheet = _pd.DataFrame()

        #------------------ Cash Flow Statement ------------------ 
        try:
            cash_flow_data = utils.get_json(ticker_url+'/cash-flow', proxy, self.session)
            data = cash_flow_data['context']['dispatcher']['stores']['FinancialTemplateStore']   # Grab the financial template store. This  details the order in which the financials should be presented.
            cash_flow_template_ttm_order, cash_flow_template_annual_order, cash_flow_level_detail = utils.build_template(data)
            
            data = cash_flow_data['context']['dispatcher']['stores']['QuoteTimeSeriesStore'] # Grab the raw financial details (this can be later combined with the financial template store detail to correctly order and present the data).
            TTM_dicts, Annual_dicts = utils.retreive_financial_details(data)
        
            TTM = _pd.DataFrame.from_dict(TTM_dicts).set_index("index")
            Annual = _pd.DataFrame.from_dict(Annual_dicts).set_index("index")
            # Combine the raw financial details and the template
            TTM = TTM.reindex(cash_flow_template_ttm_order)
            Annual = Annual.reindex(cash_flow_template_annual_order)
            TTM.columns = ['TTM ' + str(col) for col in TTM.columns] # Add 'TTM' prefix to all column names, so if combined we can tell the difference between actuals and TTM (similar to yahoo finance).
            TTM.index = TTM.index.str.replace(r'trailing', '')
            Annual.index = Annual.index.str.replace(r'annual','')
            _cash_flow_statement = Annual.merge(TTM, left_index=True, right_index=True)
            _cash_flow_statement.index = utils.camel2title(_cash_flow_statement.T)
            _cash_flow_statement['level_detail'] = cash_flow_level_detail 
            _cash_flow_statement = _cash_flow_statement.set_index([_cash_flow_statement.index,'level_detail'])
            self._cash_flow_statement = _cash_flow_statement.dropna(how='all')
        except Exception as e:
            self._cash_flow_statement = _pd.DataFrame()
        #------------------ Analysis Data/Analyst Forecasts ------------------
        try:
            analysis_data = utils.get_json(ticker_url+'/analysis',proxy,self.session)
            analysis_data = analysis_data['context']['dispatcher']['stores']['QuoteSummaryStore']        
        except Exception as e:
            analysis_data = {}
        try:
            self._analyst_trend_details = _pd.DataFrame(analysis_data['recommendationTrend']['trend'])
        except Exception as e:
            self._analyst_trend_details = _pd.DataFrame()
        try:
            self._analyst_price_target = _pd.DataFrame(analysis_data['financialData'], index=[0])[['targetLowPrice','currentPrice','targetMeanPrice','targetHighPrice','numberOfAnalystOpinions']].T
        except Exception as e:
            self._analyst_price_target = _pd.DataFrame()
        earnings_estimate = []
        revenue_estimate = []
        if len(self._analyst_trend_details) != 0:
            for key in analysis_data['earningsTrend']['trend']:
                try:
                    earnings_dict = key['earningsEstimate']
                    earnings_dict['period'] = key['period']
                    earnings_dict['endDate'] = key['endDate']
                    earnings_estimate.append(earnings_dict)
                    
                    revenue_dict = key['revenueEstimate']
                    revenue_dict['period'] = key['period']
                    revenue_dict['endDate'] = key['endDate']
                    revenue_estimate.append(revenue_dict)
                except Exception as e:
                    pass
            self._rev_est = _pd.DataFrame(revenue_estimate)
            self._eps_est = _pd.DataFrame(earnings_estimate)
        else:
            self._rev_est = _pd.DataFrame()
            self._eps_est = _pd.DataFrame()

        self._fundamentals = True

    def get_recommendations(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._recommendations
        if as_dict:
            return data.to_dict()
        return data

    def get_calendar(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._calendar
        if as_dict:
            return data.to_dict()
        return data

    def get_major_holders(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._major_holders
        if as_dict:
            return data.to_dict()
        return data

    def get_institutional_holders(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._institutional_holders
        if data is not None:
            if as_dict:
                return data.to_dict()
            return data

    def get_mutualfund_holders(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._mutualfund_holders
        if data is not None:
            if as_dict:
                return data.to_dict()
            return data

    def get_info(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._info
        if as_dict:
            return data.to_dict()
        return data

    def get_sustainability(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._sustainability
        if as_dict:
            return data.to_dict()
        return data
    
    def get_current_recommendations(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._analyst_trend_details
        if as_dict:
            return data.to_dict()
        return data
    
    def get_analyst_price_target(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._analyst_price_target
        if as_dict:
            return data.to_dict()
        return data

    def get_rev_forecast(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._rev_est
        if as_dict:
            return data.to_dict()
        return data

    def get_earnings_forecast(self, proxy=None, as_dict=False, *args, **kwargs):
        self._get_fundamentals(proxy=proxy)
        data = self._eps_est
        if as_dict:
            return data.to_dict()
        return data

    def get_earnings(self, proxy=None, as_dict=False, freq="yearly"):
        self._get_fundamentals(proxy=proxy)
        data = self._earnings[freq]
        if as_dict:
            dict_data = data.to_dict()
            dict_data['financialCurrency'] = 'USD' if 'financialCurrency' not in self._earnings else self._earnings['financialCurrency']
            return dict_data
        return data

    def get_income_statement(self, proxy=None, as_dict=False):
        self._get_fundamentals(proxy)
        data = self._income_statement
        if as_dict:
            return data.to_dict()
        return data

    def get_quarterly_income_statement(self, proxy=None, as_dict=False): # Could still be used for quarterly
        self._get_fundamentals(proxy=proxy)
        data = self._quarterly_income_statement["quarterly"]
        if as_dict:
            return data.to_dict()
        return data

    def get_balance_sheet(self, proxy=None, as_dict=False):
        self._get_fundamentals(proxy)
        data = self._balance_sheet
        if as_dict:
            return data.to_dict()
        return data

    def get_quarterly_balance_sheet(self, proxy=None, as_dict=False):   # Could still be used for quarterly
        self._get_fundamentals(proxy=proxy)
        data = self._quarterly_balance_sheet["quarterly"]
        if as_dict:
            return data.to_dict()
        return data
    
    def get_cash_flow_statement(self, proxy=None, as_dict=False):
        self._get_fundamentals(proxy=proxy)
        data = self._cash_flow_statement
        if as_dict:
            return data.to_dict()
        return data

    def get_quarterly_cash_flow_statement(self, proxy=None, as_dict=False):   # Could still be used for quarterly
        self._get_fundamentals(proxy=proxy)
        data = self._quarterly_cash_flow["quarterly"]
        if as_dict:
            return data.to_dict()
        return data

    def get_dividends(self, proxy=None):
        if self._history is None:
            self.history(period="max", proxy=proxy)
        if self._history is not None and "Dividends" in self._history:
            dividends = self._history["Dividends"]
            return dividends[dividends != 0]
        return []

    def get_splits(self, proxy=None):
        if self._history is None:
            self.history(period="max", proxy=proxy)
        if self._history is not None and "Stock Splits" in self._history:
            splits = self._history["Stock Splits"]
            return splits[splits != 0]
        return []

    def get_actions(self, proxy=None):
        if self._history is None:
            self.history(period="max", proxy=proxy)
        if self._history is not None and "Dividends" in self._history and "Stock Splits" in self._history:
            actions = self._history[["Dividends", "Stock Splits"]]
            return actions[actions != 0].dropna(how='all').fillna(0)
        return []

    def get_isin(self, proxy=None):
        # *** experimental ***
        if self._isin is not None:
            return self._isin

        ticker = self.ticker.upper()

        if "-" in ticker or "^" in ticker:
            self._isin = '-'
            return self._isin

        # setup proxy in requests format
        if proxy is not None:
            if isinstance(proxy, dict) and "https" in proxy:
                proxy = proxy["https"]
            proxy = {"https": proxy}

        q = ticker
        self.get_info(proxy=proxy)
        if "shortName" in self._info:
            q = self._info['shortName']

        url = 'https://markets.businessinsider.com/ajax/' \
              'SearchController_Suggest?max_results=25&query=%s' \
            % urlencode(q)
        data = self.session.get(
            url=url,
            proxies=proxy,
            headers=utils.user_agent_headers
        ).text

        search_str = '"{}|'.format(ticker)
        if search_str not in data:
            if q.lower() in data.lower():
                search_str = '"|'
                if search_str not in data:
                    self._isin = '-'
                    return self._isin
            else:
                self._isin = '-'
                return self._isin

        self._isin = data.split(search_str)[1].split('"')[0].split('|')[0]
        return self._isin
