import unittest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import mapped_column, Mapped

# Твои импорты
from main import app
from app_deribit.db_orm.crud_orm.crud import get_db, get_last_price
from app_deribit.db_orm.models.models import Base


# Переопределяем модель специально для SQLite тестов, из за того,
# что SQLite не справляется с полем timezone. Сделаем его строкой.
class IndexPriceTest(Base):
    """
        Test version of the IndexPriceDeribit model.

        This class is used only for testing purposes to solve SQLite compatibility issues.
        It redefines the 'created_at' column as a String instead of DateTime.
        This allows us to store ISO-formatted strings with timezone information ('Z' or '+00:00'),
        which Pydantic can successfully validate during API tests.

        Attributes:
            __tablename__: Matches the production table name to override its metadata.
            __table_args__: 'extend_existing=True' allows redefining the table structure
                            in the SQLAlchemy registry for the current test process.
        """
    __tablename__ = "index_prices_deribit"
    # параметр дает возможность внести изменения в таблицу, поскольку нам надо поменять столбец с timezone на str.
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str]
    price: Mapped[float]
    timestamp: Mapped[int]
    created_at: Mapped[str] = mapped_column()


class TestDeribitDB(unittest.IsolatedAsyncioTestCase):
    """
        Integration tests for the Deribit API and database logic.

        This class uses 'IsolatedAsyncioTestCase' to handle asynchronous calls
        to the FastAPI application and the database. It sets up a temporary
        in-memory SQLite database for each test to ensure data isolation.

        Key features:
        - Automatically creates and drops database tables for every test case.
        - Overrides the production database dependency with a test session.
        - Uses an asynchronous HTTP client to simulate API requests.
        - Tests both raw CRUD functions and FastAPI endpoints.
        """
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.TestingSessionLocal = async_sessionmaker(self.engine, expire_on_commit=False)

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async def override_get_db():
            async with self.TestingSessionLocal() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        app.dependency_overrides.clear()
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.client.aclose()
        await self.engine.dispose()

    async def _add_test_data(self):
        """Наполнение базы с использованием тестовой модели и строк"""
        async with self.TestingSessionLocal() as session:
            async with session.begin():

                now_iso = datetime.now(timezone.utc).isoformat()
                now_ts = int(datetime.now(timezone.utc).timestamp())


                p1 = IndexPriceTest(ticker="btc_usd", price=50000.0, timestamp=now_ts, created_at=now_iso)
                p2 = IndexPriceTest(ticker="btc_usd", price=51000.0, timestamp=now_ts + 300, created_at=now_iso)
                p3 = IndexPriceTest(ticker="eth_usd", price=3000.0, timestamp=now_ts, created_at=now_iso)

                session.add_all([p1, p2, p3])


    async def test_get_last_price_logic(self):
        await self._add_test_data()
        async with self.TestingSessionLocal() as session:
            result = await get_last_price(ticker="btc_usd", session=session)
            self.assertIsNotNone(result)
            self.assertEqual(result.price, 51000.0)

    async def test_get_last_db_price_endpoint(self):
        await self._add_test_data()
        response = await self.client.get("/api/prices/last", params={"ticker": "btc_usd"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ticker"], "btc_usd")
        self.assertEqual(float(data["price"]), 51000.0)

    async def test_get_date_between_endpoint(self):
        await self._add_test_data()
        query_params = {
            "ticker": "btc_usd",
            "start_year": 2020, "start_month": 1, "start_day": 1, "start_hour": 0, "start_minute": 0,
            "end_year": 2030, "end_month": 1, "end_day": 1, "end_hour": 0, "end_minute": 0
        }
        response = await self.client.get("/api/prices/period", params=query_params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    async def test_get_last_price_not_found(self):
        valid_but_empty_ticker = "eth_usd"  # Или любой другой из твоего списка Ticker

        response = await self.client.get("/api/prices/last", params={"ticker": valid_but_empty_ticker})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json() is None or response.json() == [])
