Change Log
===========
0.1.64
------
- Updated the way in which the annual financial data is pieced together (income statement, balance sheet and cash flow statement) this now more accurately reflects what is presented in Yahoo Finance.
- Added functionality to enable users to pull in detail from the Yahoo Finance Analysis page.

0.1.63
------
- Duplicates and missing rows cleanup

0.1.62
------
- Added UserAgent to all requests (via ```utils.user_agent_headers```)

0.1.61
------
- Switched to using ```query2.finance.yahoo.com```, which used HTTP/1.1

0.1.60
------
- Gracefully fail on misc operations (options, auto/back adjustments, etc)
- Added financial data to ```info()```
- Using session headers
- Get price even if open price not available
- Argument added for silencing error printing
- Merged PRs to fix some bugs

0.1.59
------
- Added custom requests session instance support in holders

0.1.58
------
- Allow specifying a custom requests session instance

0.1.57
------
- Added Conversion rate hint using 'financialCurrency' property in earnings
- Add important try+catch statements
- Fixed issue with 1 hour interval
- Merged PRs to fix some bugs
- Fixed issue with special characters in tickers

0.1.56
------
- Updated numpy version
- Merged PRs to fix some bugs

0.1.55
------
- Fixed institutional investors and mutual fund holders issue (#459)
- Fix for UTC timestamps in options chains (#429)

0.1.54
------
- ISIN lookup working with intl. tickers

0.1.53
------
- Added ``Ticker.isin`` + ``Ticker.get_isin(...)``. This is still experimental. Do not rely on it for production.
- Bug fixed: holders were always returning results for MSFT

0.1.52
------
- Improved JSON regex parsing

0.1.51
------
- Added holdings data (``Ticker.major_holders`` and ``Ticker.institutional_holders``)
- Added logo url to ``Ticker.info``
- Handling different date formats in fundamentals
- Faster JSON parsing using regex
- Trying to re-download JSON twice before giving up
- Using ujson instead of json if installed
- Fixed (more) ``ticker.info`` issues
- Misc bugfixes

0.1.50
------
- Fixed ``ticker.info`` issues
- Handle sustainability index error
- Added test script based on @GregoryMorse's pull request

0.1.49
------
- Fixed ``elementwise comparison`` warning

0.1.48
------
- Fixed issues related to non-publicly traded tickers (crypto, currency, etc)

0.1.47
------
- Fixed options-related bug that was caused by code refactoring

0.1.46
------
- Rerwote all fundamental-related methods, which now support quarterly financials, cashflow, balance sheets, and earnings, analysts recommendations, and earnings calendar data
- Code refactoring

0.1.45
------
- Added sustainability data/error handling for ETF/MF (by GregoryMorse)
- Avoid rounding the values retrieved from Yahoo by default (by aglebov)
- Added 'rename=True' for the namedtuple (raffieeey)

0.1.44
------
- Improved ``Tickers`` module (see https://github.com/ranaroussi/yfinance/issues/86)
- Misc bugfixes

0.1.43
------
- Bugfixes

0.1.42
------
- Fix data realignment when Yahoo returns with missing/malform data

0.1.41
------
- Added methods for downloading option chain

0.1.40
------
- Fixed issue related to threads when downloading many symbols
- Fix issue relared to missing data

0.1.39
------
- Added ``Ticker('XXX').financials``, ``Ticker('XXX').balance_sheet``, and ``Ticker('XXX').cashflow``
- Proxy can be used when downloading actions

0.1.38
------
- Making sure tickers are always uppercase
- Added Tickers to ``__all__``
- Updated readme to reflect current library structure

0.1.37
------
- Overriding old ``pandas_datareader.data.DataReader`` when calling ``pdr_override()``
- ``Tickers()`` returns a named tuple of ``Ticker()`` objects

0.1.36
------
- Package renamed to ``yfinance``
- Added option to specify proxy server

0.1.35
------
- Updated requirements

0.1.34
------
- Intercept yahoo "site down" message
- Better period handling
- Threading is True by default

0.1.33
------
- Better error handling

0.1.32
------
- Better error handling
- Updated min. versions for requirements

0.1.31
------
- Include ticker in error message if error is raised

0.1.30
------
- Fixed Yahoo!'s 30m bars being returned as 60m/15m

0.1.29
------
- Fixed issue with Pandas "DataFrame constructor not properly called!"
- If ``threads`` is set to True, it will default to number of tickers (max = @ of CPU cores)

0.1.28
------
- Threading defaults to ``False``

0.1.27
------
- Threading is back :)

0.1.26
------
- Fixed weird bug with Yahoo!, which is returning 60m interval when requesting for 30m interval, by requesting 15m interval and resampling the returned data
- ``Ticker.history()`` auto-adjusts data by default

0.1.21 - 0.1.25
------
- Bugfixs

0.1.2
------
- Round prices based on metadata decimals

0.1.1
------
- Setting Volume colume as np.int64 dtype to avoid integer overflow on Windows

0.1.0
-------
- Works with v8 API
- Introduced Ticker module
- Complete re-write of the entire code
- Skipped a bunch of version :)

0.0.22
-------
- Deprecated Panel support

0.0.21
-------
- Code cleanup

0.0.20
-------
- Fixed issue with progress bar (issue #42)

0.0.19
-------
- Misc bugfixes

0.0.18
-------
- Minor Bugfixes
- Added deprecation warning for future versions regarding auto-overriding pandas_datareader

0.0.17
-------
- Handles duplicate index

0.0.16
-------
- Progress bar bugfix

0.0.15
-------
- Bugfix (closing issue #11)

0.0.14
-------
- Added support for Python 2.7
- Confirming valid data returned before adding it to ``_DFS_``

0.0.13
-------
- Removed debugging code

0.0.12
-------
- Minor bug fix (closing #6)

0.0.11
-------
- Downloads ONLY dividend and stock splits data using ``actions='only'``)

0.0.10
-------
- Downloads dividend and stock splits data (use ``actions=True``)

0.0.9
-------
- Add ``threads`` parameter to ``download()`` (# of threads to use)

0.0.8
-------
- Removed 5 second wait for every failed fetch
- Reduced TTL for Yahoo!'s cookie
- Keeps track of failed downloads and tries to re-download all failed downloads one more time before giving up
- Added progress bar (can be turned off useing ``progress=False``)

0.0.7
-------
- ``pandas_datareader`` is optional (can be called via ``download()`` or via ``pdr.get_data_yahoo()``)
- Tries to re-fetch Yahoo cookie in case of timeout/error

0.0.6
-------
- Forcing index to be of datetime type

0.0.5
-------
- Works using ``requests`` = no need for Selenium, PyVirtualDisplay, or Chrome Driver

0.0.4
-------
- Removed ALL debugging code :)

0.0.3
-------
- Removed debugging code

0.0.2
-------
- Option to explicitly specify the location of the Chrome driver

0.0.1
-------
- Initial release (alpha)
