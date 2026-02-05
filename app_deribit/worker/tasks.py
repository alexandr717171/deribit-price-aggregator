"""
Celery Task Definitions.

This module defines the background tasks executed by the Celery worker.
It acts as a bridge between the synchronous Celery worker and
the asynchronous aiohttp fetching logic.
"""

import asyncio

from app_deribit.worker.celery_app import app
from app_deribit.services_aiohttp.request_to import get_prices


@app.task(bind=True, max_retries=3)
def create_all_prices(self):
    """
        Background task to trigger the price fetching process.

        Since Celery workers are typically synchronous, this task uses
        'asyncio.run' to execute the asynchronous 'get_prices' function.

        Features:
        - bind=True: Allows the task to access its own instance (self).
        - max_retries=3: Automatically retries the task up to 3 times in case of failure.
        """
    try:
        # Running the asynchronous scraping logic inside the synchronous task
        return asyncio.run(get_prices())
    except Exception as exc:
        # Retries the task if an error occurs (e.g., network issues)
        raise self.retry(exc=exc)
