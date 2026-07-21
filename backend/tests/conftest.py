import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_db
from app.core.config import settings
from app.db.base import Base
from app.main import app


TEST_DATABASE_URL = settings.TEST_DATABASE_URL


# Safety guard:
# Never allow pytest to use the development database.
if "orchestrix_test" not in TEST_DATABASE_URL:
    raise RuntimeError(
        "Unsafe test configuration: "
        "pytest must use orchestrix_test."
    )


test_engine = create_engine(
    TEST_DATABASE_URL
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create the schema in orchestrix_test before
    the test session starts.

    Remove the schema after all tests finish.
    """

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )

@pytest.fixture(autouse=True)
def clean_test_database():
    """
    Clean all application tables before every test.

    This guarantees that committed data from one test
    cannot affect another test.
    """

    with test_engine.begin() as connection:

        for table in reversed(
            Base.metadata.sorted_tables
        ):
            connection.execute(
                table.delete()
            )

    yield


@pytest.fixture
def db_session():
    """
    Provide a database session connected only
    to orchestrix_test.
    """

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(db_session):
    """
    Override the application's get_db dependency
    so TestClient requests use orchestrix_test.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = (
        override_get_db
    )

    try:
        with TestClient(
            app,
            raise_server_exceptions=False,
        ) as test_client:
            yield test_client

    finally:
        app.dependency_overrides.clear()