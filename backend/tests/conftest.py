import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    from sqlalchemy import text

    from app.db.database import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:  # pragma: no cover
        pytest.skip(f"PostgreSQL no disponible (inicia con: docker compose up -d db y corre la seed): {e}")
    return TestClient(app)


@pytest.fixture(scope="session")
def token_admin(client):
    resp = client.post(
        "/api/v1/auth/login", data={"username": "admin@autogest.co", "password": "Admin.123"}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def token_cliente(client):
    resp = client.post(
        "/api/v1/auth/login", data={"username": "cliente@autogest.co", "password": "Client.123"}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def auth_admin(token_admin):
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture()
def auth_cliente(token_cliente):
    return {"Authorization": f"Bearer {token_cliente}"}