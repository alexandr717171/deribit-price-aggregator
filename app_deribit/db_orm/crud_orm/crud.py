"""
Database operations for Deribit index prices.

This module provides CRUD functions to fetch data,
filter by ticker/date, and insert new price records.
"""
from datetime import datetime
from typing import Sequence, AsyncGenerator, Annotated

from fastapi import Depends, Query
from sqlalchemy import select, NullPool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app_deribit.core.config_engine import async_session
from app_deribit.core.config_env_variable import db_url
from app_deribit.db_orm.models.models import IndexPriceDeribit
from app_deribit.pydantc_models.models import DeribitTimeZone, DateFilterStart, DateFilterEnd
from app_deribit.services_aiohttp.config_data_aiohttp import Ticker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session



async def get_all_by_ticker(
        ticker: Ticker,
        session: Annotated[AsyncSession,Depends(get_db)],
        limit: Annotated[int, Query(ge=1, description='The maximum number of records to return.')] = 100,
) -> Sequence[IndexPriceDeribit]:
    """
    Get all stored records for a specific currency ticker.

    Args:
        session: Async database session.
        ticker: The currency ticker (e.g., 'BTC_USD').
        limit: The maximum number of records to return.

    Returns:
        A list of IndexPriceDeribit objects.
    """
    query = (select(IndexPriceDeribit)
             .where(IndexPriceDeribit.ticker == ticker)
             .order_by(IndexPriceDeribit.timestamp.desc())
             .limit(limit))
    result = await session.scalars(query)
    return result.all()


async def get_last_price(
        ticker: Ticker,
        session: Annotated[AsyncSession,Depends(get_db)],
) -> IndexPriceDeribit | None:
    """
    Get the most recent price for a specific ticker.

    Args:
        session: Async database session.
        ticker: The currency ticker.

    Returns:
        The latest IndexPriceDeribit object or None if not found.
    """
    query = (
        select(IndexPriceDeribit)
        .where(IndexPriceDeribit.ticker == ticker)
        .order_by(IndexPriceDeribit.timestamp.desc())
        .limit(1)
    )
    return await session.scalar(query)


async def get_by_date(
        session: Annotated[AsyncSession,Depends(get_db)],
        ticker: Ticker,
        start: Annotated[DateFilterStart, Depends()],
        end: Annotated[DateFilterEnd, Depends()],
        limit: Annotated[int, Query(ge=1,
                                    description='The maximum number of records to return.'
                                    )] = 100) -> Sequence[IndexPriceDeribit]:
    """
    Get prices by filtering the datetime created_at field.
    This is very fast because of the 'ix_ticker_timestamp' index.
    """
    query = (
        select(IndexPriceDeribit)
        .where(IndexPriceDeribit.ticker == ticker)
        .where(IndexPriceDeribit.created_at.between(start.dt_object, end.dt_end_object))
        .order_by(IndexPriceDeribit.timestamp.asc())
        .limit(limit)
    )
    result = await session.scalars(query)

    return result.all()


async def insert_data(data: dict):
    """
    Create a new record in the IndexPriceDeribit table.

    This function is designed specifically for Celery workers.
    It creates a local engine with NullPool to avoid 'Different Event Loop' errors
    and ensures that database connections are closed immediately after use.

    Args:
        data: A dictionary containing the fields for IndexPriceDeribit.

    Returns:
        The validated DeribitTimeZone model instance.

    Raises:
        SQLAlchemyError: If there is an issue with the database transaction.
    """
    async_engine = create_async_engine(url=db_url, poolclass=NullPool)
    async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        try:

            async with session.begin():
                index_price = IndexPriceDeribit(**data)
                session.add(index_price)
                await session.flush()

                result = DeribitTimeZone.model_validate(index_price)
            return result
        except SQLAlchemyError as e:
            print(e)
            raise


