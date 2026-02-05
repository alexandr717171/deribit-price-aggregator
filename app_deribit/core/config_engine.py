"""
Database configuration and session management.

This module initializes the asynchronous SQLAlchemy engine using the
database URL from environment variables. It provides an 'async_sessionmaker'
to handle asynchronous database transactions throughout the application.
"""

from app_deribit.core.config_env_variable import db_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(url=db_url)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)








