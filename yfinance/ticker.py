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

# import time as _time
import datetime as _datetime
import requests as _requests
import pandas as _pd
# import numpy as _np

# import json as _json
# import re as _re
from collections import namedtuple as _namedtuple

from . import utils
from .base import TickerBase


class Ticker(TickerBase):

    def __repr__(self):
        return 'yfinance.Ticker object <%s>' % self.ticker

    def _download_options(self, date=None, proxy=None):
        if date is None:
            url = "{}/v7/finance/options/{}".format(
                self._base_url, self.ticker)
        else:
            url = "{}/v7/finance/options/{}?date={}".format(
                self._base_url, self.ticker, date)

        # setup proxy in requests format
        if proxy is not None:
            if isinstance(proxy, dict) and "https" in proxy:
                proxy = proxy["https"]
            proxy = {"https": proxy}

        r = _requests.get(
            url=url,
            proxies=proxy,
            headers=utils.user_agent_headers
        ).json()
        if len(r.get('optionChain', {}).get('result', [])) > 0:
            for exp in r['optionChain']['result'][0]['expirationDates']:
                self._expirations[_datetime.datetime.utcfromtimestamp(
                    exp).strftime('%Y-%m-%d')] = exp
            opt = r['optionChain']['result'][0].get('options', [])
            return opt[0] if len(opt) > 0 else []

    def _options2df(self, opt, tz=None):
        data = _pd.DataFrame(opt).reindex(columns=[
            'contractSymbol',
            'lastTradeDate',
            'strike',
            'lastPrice',
            'bid',
            'ask',
            'change',
            'percentChange',
            'volume',
            'openInterest',
            'impliedVolatility',
            'inTheMoney',
            'contractSize',
            'currency'])

        data['lastTradeDate'] = _pd.to_datetime(
            data['lastTradeDate'], unit='s')
        if tz is not None:
            data['lastTradeDate'] = data['lastTradeDate'].tz_localize(tz)
        return data

    def option_chain(self, date=None, proxy=None, tz=None):
        if date is None:
            options = self._download_options(proxy=proxy)
        else:
            if not self._expirations:
                self._download_options()
            if date not in self._expirations:
                raise ValueError(
                    "Expiration `%s` cannot be found. "
                    "Available expiration are: [%s]" % (
                        date, ', '.join(self._expirations)))
            date = self._expirations[date]
            options = self._download_options(date, proxy=proxy)

        return _namedtuple('Options', ['calls', 'puts'])(**{
            "calls": self._options2df(options['calls'], tz=tz),
            "puts": self._options2df(options['puts'], tz=tz)
        })

    # ------------------------

    @property
    def isin(self):
        return self.get_isin()

    @property
    def major_holders(self):
        return self.get_major_holders()

    @property
    def institutional_holders(self):
        return self.get_institutional_holders()

    @property
    def mutualfund_holders(self):
        return self.get_mutualfund_holders()

    @property
    def dividends(self):
        return self.get_dividends()

    @property
    def splits(self):
        return self.get_splits()

    @property
    def actions(self):
        return self.get_actions()

    @property
    def info(self):
        return self.get_info()

    @property
    def calendar(self):
        return self.get_calendar()

    @property
    def recommendations(self):
        return self.get_recommendations()

    @property
    def earnings(self):
        return self.get_earnings()

    @property
    def quarterly_earnings(self):
        return self.get_earnings(freq='quarterly')

    @property
    def income_statement(self):
        return self.get_income_statement()

    @property
    def quarterly_income_statement(self):
        return self.get_quarterly_income_statement()

    @property
    def balance_sheet(self):
        return self.get_balance_sheet()

    @property
    def quarterly_balance_sheet(self):
        return self.get_quarterly_balance_sheet()

    @property
    def cash_flow_statement(self):
        return self.get_cash_flow_statement()

    @property
    def quarterly_cash_flow_statement(self):
        return self.get_quarterly_cash_flow_statement()

    @property
    def sustainability(self):
        return self.get_sustainability()

    @property
    def current_recommendations(self):
        return self.get_current_recommendations()

    @property
    def analyst_price_target(self):
        return self.get_analyst_price_target()

    @property
    def revenue_forecasts(self):
        return self.get_rev_forecast()

    @property
    def earnings_forecasts(self):
        return self.get_earnings_forecast()

    @property
    def options(self):
        if not self._expirations:
            self._download_options()
        return tuple(self._expirations.keys())
