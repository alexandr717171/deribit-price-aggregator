"""
Asynchronous Data Fetching Service.

This module handles concurrent HTTP requests to the Deribit API using 'aiohttp'.
It performs the following operations:
- Fetches real-time index prices for multiple cryptocurrency tickers.
- Processes API responses and extracts price and timestamp data.
- Validates data using Pydantic models.
- Asynchronously saves the retrieved data into the database.
"""
import asyncio
import aiohttp

from app_deribit.db_orm.crud_orm.crud import insert_data
from app_deribit.pydantc_models.models import DeribitTimeZone
from app_deribit.services_aiohttp.config_data_aiohttp import get_url, ticker_tuple


async def fetch_price(session: aiohttp.ClientSession,
                      ticker: str,
                      param: str = 'get_index_price',
                      query: str = 'index_name') -> DeribitTimeZone:
    """
    Fetches the price for a single ticker and saves it to the database.

    Args:
        session: An active aiohttp client session.
        ticker: The currency pair (e.g., 'btc_usd').
        param: API method name.
        query: Query parameter name.

    Returns:
        The created database object (DeribitTimeZone).
    """
    url = get_url(ticker, param, query)
    async with session.get(url) as response:
        response.raise_for_status()
        data = await response.json()
        result = data.get('result', {})
        price = result.get('index_price')
        timestamp = data.get('usOut')
        print(f"Цена {ticker.upper()}: {price}, timestamp: {timestamp}")
        data_db = {'price': price, 'timestamp': timestamp, 'ticker': ticker}
        object_db = await insert_data(data_db)
        return object_db



async def get_prices(tickers: tuple = ticker_tuple):
    """
        Orchestrates concurrent fetching of multiple tickers.
        Uses asyncio.gather to run requests in parallel for better performance.
        """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, ticker) for ticker in tickers]
        result = await asyncio.gather(*tasks)
        return result


