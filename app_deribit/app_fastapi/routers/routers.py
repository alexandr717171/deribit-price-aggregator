"""
API Routes Module for Deribit Index Prices.

This module defines the FastAPI endpoints for retrieving cryptocurrency price data.
It handles requests for:
- Fetching all historical data for a specific ticker.
- Retrieving the most recent (last) price from the database.
- Filtering price records by a custom date and time range.

All endpoints use dependency injection for database operations and
Pydantic models for response serialization.
"""

from typing import Sequence, Any, Optional, Annotated
from fastapi import APIRouter, Depends
from app_deribit.db_orm.crud_orm.crud import get_all_by_ticker, get_last_price, get_by_date
from app_deribit.db_orm.models.models import IndexPriceDeribit
from app_deribit.pydantc_models.models import DeribitTimeZone

api_router = APIRouter()

@api_router.get("/prices", tags=["prices"], response_model=list[DeribitTimeZone])
async def get_all_prices(
        all_db_data: Annotated[Sequence[IndexPriceDeribit], Depends(get_all_by_ticker)
        ]) -> Any:
    """
    Get all stored records for a specific currency ticker.
    Returns a list of price records from the database.
    """
    return all_db_data


@api_router.get("/prices/last", response_model=Optional[DeribitTimeZone])
async def get_last_db_price(
        last_price: Annotated[IndexPriceDeribit | None, Depends(get_last_price)
        ]) -> Any:
    """
    Get the most recent price record for a specific ticker.
    Returns the latest price object or null if no data exists.
    """
    return last_price

@api_router.get("/prices/period", tags=["prices"], response_model=list[DeribitTimeZone])
async def get_date_between(
        all_data_between: Annotated[Sequence[IndexPriceDeribit], Depends(get_by_date)
        ]) -> Any:
    """
    Get price records within a specific date and time range.
    Filter data using start and end parameters (year, month, day, etc.).
    """
    return all_data_between
