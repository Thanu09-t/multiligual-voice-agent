import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow():
    await init_db()
    unique_email = f"agent.nova_{uuid.uuid4().hex[:6]}@example.com"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register with too-short password -> should fail
        bad_reg = await client.post(
            "/api/auth/register",
            json={"email": f"short_{uuid.uuid4().hex[:6]}@test.com", "password": "123", "full_name": "Short"},
        )
        assert bad_reg.status_code == 400

        # 2. Valid Registration
        reg_resp = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "strongPassword123",
                "full_name": "Nova Agent",
            },
        )
        assert reg_resp.status_code == 200
        reg_data = reg_resp.json()
        assert "access_token" in reg_data
        assert reg_data["email"] == unique_email
        token = reg_data["access_token"]

        # 3. Duplicate email -> should fail
        dup_resp = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "strongPassword123",
                "full_name": "Nova Agent Duplicate",
            },
        )
        assert dup_resp.status_code == 400

        # 4. Login with invalid password -> should fail
        bad_login = await client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "wrongPassword"},
        )
        assert bad_login.status_code == 401

        # 5. Login with correct password
        login_resp = await client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "strongPassword123"},
        )
        assert login_resp.status_code == 200
        login_token = login_resp.json()["access_token"]

        # 6. Profile fetch using Bearer token
        headers = {"Authorization": f"Bearer {login_token}"}
        me_resp = await client.get("/api/auth/me", headers=headers)
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["email"] == unique_email
        assert me_data["full_name"] == "Nova Agent"

        # 7. Unauthenticated request -> should fail
        unauth_resp = await client.get("/api/auth/me")
        assert unauth_resp.status_code == 401
