#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Yahoo! Finance market data downloader (+fix for Pandas Datareader)
# https://github.com/ranaroussi/yfinance

"""
Sanity check for most common library uses all working
- Stock: Microsoft
- ETF: Russell 2000 Growth
- Mutual fund: Vanguard 500 Index fund
- Index: S&P500
- Currency BTC-USD
"""

import yfinance as yf
import unittest

symbols = ['MSFT', 'IWO', 'VFINX', '^GSPC', 'BTC-USD']
tickers = [yf.Ticker(symbol) for symbol in symbols]


class TestTicker(unittest.TestCase):
    def test_info_history(self):
        for ticker in tickers:
            # always should have info and history for valid symbols
            assert(ticker.info is not None and ticker.info != {})
            assert(ticker.history(period="max").empty is False)

    def test_attributes(self):
        for ticker in tickers:
            ticker.isin
            ticker.major_holders
            ticker.institutional_holders
            ticker.mutualfund_holders
            ticker.dividends
            ticker.splits
            ticker.actions
            ticker.info
            ticker.calendar
            ticker.recommendations
            ticker.earnings
            ticker.quarterly_earnings
            ticker.income_statement
            ticker.quarterly_income_statement
            ticker.balance_sheet
            ticker.quarterly_balance_sheet
            ticker.cash_flow_statement
            ticker.quarterly_cash_flow_statement
            ticker.sustainability
            ticker.current_recommendations
            ticker.analyst_price_target
            ticker.revenue_forecasts
            ticker.earnings_forecasts
            ticker.options

    def test_holders(self):
        for ticker in tickers:
            assert(ticker.info is not None and ticker.info != {})
            assert(ticker.major_holders is not None)
            assert(ticker.institutional_holders is not None)


if __name__ == '__main__':
    unittest.main()
