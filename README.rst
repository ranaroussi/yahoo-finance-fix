Yahoo! Finance market data downloader
=====================================

.. image:: https://img.shields.io/badge/python-2.7,%203.4+-blue.svg?style=flat
    :target: https://pypi.python.org/pypi/yfinance
    :alt: Python version

.. image:: https://img.shields.io/pypi/v/yfinance.svg?maxAge=60
    :target: https://pypi.python.org/pypi/yfinance
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/status/yfinance.svg?maxAge=60
    :target: https://pypi.python.org/pypi/yfinance
    :alt: PyPi status

.. image:: https://img.shields.io/pypi/dm/yfinance.svg?maxAge=2592000&label=installs&color=%2327B1FF
    :target: https://pypi.python.org/pypi/yfinance
    :alt: PyPi downloads

.. image:: https://img.shields.io/travis/ranaroussi/yfinance/main.svg?maxAge=1
    :target: https://travis-ci.com/ranaroussi/yfinance
    :alt: Travis-CI build status

.. image:: https://www.codefactor.io/repository/github/ranaroussi/yfinance/badge
    :target: https://www.codefactor.io/repository/github/ranaroussi/yfinance
    :alt: CodeFactor

.. image:: https://img.shields.io/github/stars/ranaroussi/yfinance.svg?style=social&label=Star&maxAge=60
    :target: https://github.com/ranaroussi/yfinance
    :alt: Star this repo

.. image:: https://img.shields.io/twitter/follow/aroussi.svg?style=social&label=Follow&maxAge=60
    :target: https://twitter.com/aroussi
    :alt: Follow me on twitter

\

Ever since `Yahoo! finance <https://finance.yahoo.com>`_ decommissioned
their historical data API, many programs that relied on it to stop working.

**yfinance** aims to solve this problem by offering a reliable, threaded,
and Pythonic way to download historical market data from Yahoo! finance.


NOTE
~~~~

The library was originally named ``fix-yahoo-finance``, but
I've since renamed it to ``yfinance`` as I no longer consider it a mere "fix".
For reasons of backward-compatibility, ``fix-yahoo-finance`` now import and
uses ``yfinance``, but you should install and use ``yfinance`` directly.

`Changelog » <./CHANGELOG.rst>`__

-----

==> Check out this `Blog post <https://aroussi.com/#post/python-yahoo-finance>`_ for a detailed tutorial with code examples.

-----

Quick Start
===========

The Ticker module
~~~~~~~~~~~~~~~~~

The ``Ticker`` module, which allows you to access
ticker data in a more Pythonic way:

Note: yahoo finance datetimes are received as UTC.

.. code:: python

    import yfinance as yf

    msft = yf.Ticker("MSFT")

    # get stock info
    msft.info

    # get historical market data
    hist = msft.history(period="max")

    # show actions (dividends, splits)
    msft.actions

    # show dividends
    msft.dividends

    # show splits
    msft.splits

    # show income statement
    msft.income_statement
    msft.quarterly_income_statement

    # show major holders
    msft.major_holders

    # show institutional holders
    msft.institutional_holders

    # show balance sheet
    msft.balance_sheet
    msft.quarterly_balance_sheet

    # show cash flow statement
    msft.cash_flow_statement
    msft.quarterly_cash_flow_statement

    # show earnings
    msft.earnings
    msft.quarterly_earnings

    # show sustainability
    msft.sustainability

    # show analysts recommendations
    msft.recommendations

    # show next event (earnings, etc)
    msft.calendar

    # show ISIN code - *experimental*
    # ISIN = International Securities Identification Number
    msft.isin

    # show options expirations
    msft.options

    # get option chain for specific expiration
    opt = msft.option_chain('YYYY-MM-DD')
    # data available via: opt.calls, opt.puts

    # get analyst recommendation trends (count of analysts recommending strong buy, buy, hold, sell, strong sell over the last few months)
    msft.current_recommendations

    # get analyst price targets (share price low estimate, current price, mean estimate, high estimate and number of analysts providing estimates)
    msft.analyst_price_target

    # get analyst revenue forecasts
    msft.revenue_forecasts
    
    # get analyst earnings forecasts
    msft.earnings_forecasts

If you want to use a proxy server for downloading data, use:

.. code:: python

    import yfinance as yf

    msft = yf.Ticker("MSFT")

    msft.history(..., proxy="PROXY_SERVER")
    msft.get_actions(proxy="PROXY_SERVER")
    msft.get_dividends(proxy="PROXY_SERVER")
    msft.get_splits(proxy="PROXY_SERVER")
    msft.get_balance_sheet(proxy="PROXY_SERVER")
    msft.get_cash_flow_statement(proxy="PROXY_SERVER")
    msft.option_chain(..., proxy="PROXY_SERVER")
    ...

To use a custom ``requests`` session (for example to cache calls to the API
or customize the ``User-agent`` header), pass a ``session=`` argument to the
Ticker constructor.

.. code:: python

    import requests_cache
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = 'my-program/1.0'
    ticker = yf.Ticker('msft aapl goog', session=session)
    # The scraped response will be stored in the cache
    ticker.actions

To initialize multiple ``Ticker`` objects, use

.. code:: python

    import yfinance as yf

    tickers = yf.Tickers('msft aapl goog')
    # ^ returns a named tuple of Ticker objects

    # access each ticker using (example)
    tickers.tickers.MSFT.info
    tickers.tickers.AAPL.history(period="1mo")
    tickers.tickers.GOOG.actions


Fetching data for multiple tickers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import yfinance as yf
    data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")


I've also added some options to make life easier :)

.. code:: python

    data = yf.download(  # or pdr.get_data_yahoo(...
            # tickers list or string as well
            tickers = "SPY AAPL MSFT",

            # use "period" instead of start/end
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # (optional, default is '1mo')
            period = "ytd",

            # fetch data by interval (including intraday if period < 60 days)
            # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            # (optional, default is '1d')
            interval = "1m",

            # group by ticker (to access via data['SPY'])
            # (optional, default is 'column')
            group_by = 'ticker',

            # adjust all OHLC automatically
            # (optional, default is False)
            auto_adjust = True,

            # download pre/post regular market hours data
            # (optional, default is False)
            prepost = True,

            # use threads for mass downloading? (True/False/Integer)
            # (optional, default is True)
            threads = True,

            # proxy URL scheme use use when downloading?
            # (optional, default is None)
            proxy = None
        )


Managing Multi-Level Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following answer on Stack Overflow is for `How to deal with multi-level column names downloaded with yfinance? <https://stackoverflow.com/questions/63107801>`_

* ``yfinance`` returns a ``pandas.DataFrame`` with multi-level column names, with a level for the ticker and a level for the stock price data

  * The answer discusses:

    * How to correctly read the the multi-level columns after saving the dataframe to a csv with ``pandas.DataFrame.to_csv``
    * How to download single or multiple tickers into a single dataframe with single level column names and a ticker column


``pandas_datareader`` override
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your code uses ``pandas_datareader`` and you want to download data faster,
you can "hijack" ``pandas_datareader.data.get_data_yahoo()`` method to use
**yfinance** while making sure the returned data is in the same format as
**pandas_datareader**'s ``get_data_yahoo()``.

.. code:: python

    from pandas_datareader import data as pdr

    import yfinance as yf
    yf.pdr_override() # <== that's all it takes :-)

    # download dataframe
    data = pdr.get_data_yahoo("SPY", start="2017-01-01", end="2017-04-30")


Installation
------------

Install ``yfinance`` using ``pip``:

.. code:: bash

    $ pip install yfinance --upgrade --no-cache-dir


To install ``yfinance`` using ``conda``, see `this <https://anaconda.org/ranaroussi/yfinance>`_.

Requirements
------------

* `Python <https://www.python.org>`_ >= 2.7, 3.4+
* `Pandas <https://github.com/pydata/pandas>`_ (tested to work with >=0.23.1)
* `Numpy <http://www.numpy.org>`_ >= 1.11.1
* `requests <http://docs.python-requests.org/en/master/>`_ >= 2.14.2
* `lxml <https://pypi.org/project/lxml/>`_ >= 4.5.1

Optional (if you want to use ``pandas_datareader``)
---------------------------------------------------

* `pandas_datareader <https://github.com/pydata/pandas-datareader>`_ >= 0.4.0

Legal Stuff
------------

**yfinance** is distributed under the **Apache Software License**. See the `LICENSE.txt <./LICENSE.txt>`_ file in the release for details.


P.S.
------------

Please drop me an note with any feedback you have.

**Ran Aroussi**
