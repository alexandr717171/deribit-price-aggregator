"""
ACelery Task Utilities and API Constants.

This module provides helper functions and constants for the Celery background
worker. It specifically supports aiohttp-based data fetching from the
Deribit API, ensuring that requests are formatted correctly.

This module defines supported cryptocurrency tickers using Enum for strict
validation and provides a helper function to construct Deribit API endpoints.
"""
from enum import Enum
# список валют используется в модуле request_to.
ticker_tuple = ('btc_usd', 'eth_usd')

class Ticker(str, Enum):
    BTC_USD = 'btc_usd'
    ETH_USD = 'eth_usd'


def get_url(ticker: str, param: str = 'get_index_price', query: str = 'index_name')-> str:
    """
    Constructs the target URL for aiohttp requests within Celery tasks.

    Args:
        ticker: The currency pair to fetch.
        param: The specific Deribit API method.
        query: The ticker parameter name (default is 'index_name').

    Returns:
        The full API endpoint URL as a string.
    """
    return f'https://test.deribit.com/api/v2/public/{param}?{query}={ticker}'
