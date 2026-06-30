import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import get_db
from app.main import app


def register_user(client: TestClient, email: str, full_name: str = "Test User") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": full_name,
        },
    )
    assert response.status_code == 201
    data = response.json()
    return {
        "Authorization": f"Bearer {data['access_token']}",
        "refresh_token": data["refresh_token"],
    }


@pytest.fixture()
def auth_headers(client):
    return register_user(client, "workspace-user@devhub.ai")


@pytest.fixture()
def other_user_headers(client):
    return register_user(client, "other-user@devhub.ai", "Other User")


@pytest.fixture()
def db_engine():
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
