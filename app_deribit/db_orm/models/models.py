"""
SQLAlchemy database models definition.

This module contains the database schema using SQLAlchemy 2.0's Declarative style.
It defines the 'IndexPriceDeribit' table to store cryptocurrency index prices
with high-precision numeric values and performance-optimized indexes.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, Numeric, BigInteger, DateTime, func, Index
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(AsyncAttrs, DeclarativeBase):
    """
     Abstract base class for all models, including AsyncAttrs
     to support asynchronous attribute access.
     """
    __abstract__ = True

class IndexPriceDeribit(Base):
    """
    Model representing Deribit index prices in the database.

    Fields:
        id: Unique identifier (Primary Key).
        ticker: Currency pair symbol (e.g., btc_usd).
        price: High-precision price value (16 digits total, 8 after decimal).
        timestamp: Unix timestamp for the price record.
        created_at: Database-generated timestamp with timezone info.
    """
    __tablename__ = 'index_prices_deribit'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(10))
    price: Mapped[Decimal] = mapped_column(Numeric(16, 8))
    timestamp: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        Index('ix_ticker_timestamp', 'ticker', 'timestamp'),
        Index('ix_ticker_created_at', 'ticker', 'created_at'),
    )
