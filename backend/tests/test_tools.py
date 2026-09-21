import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db
from app.tools.calculator import CalculatorTool
from app.tools.weather import WeatherTool
from app.tools.web_search import WebSearchTool


@pytest.mark.asyncio
async def test_calculator_direct():
    calc = CalculatorTool()
    res1 = await calc.execute(expression="25% of 840")
    assert res1["result"] == 210

    res2 = await calc.execute(expression="(12 * 4) + 10")
    assert res2["result"] == 58


@pytest.mark.asyncio
async def test_weather_direct():
    weather = WeatherTool()
    res = await weather.execute(location="Tokyo")
    assert "location" in res
    assert "temperature_c" in res


@pytest.mark.asyncio
async def test_web_search_direct():
    search = WebSearchTool()
    res = await search.execute(query="Artificial Intelligence")
    assert "results" in res
    assert len(res["results"]) > 0


@pytest.mark.asyncio
async def test_agent_tool_usage_calculator():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"message": "What is 25% of 840?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "210" in data["display_text"]


@pytest.mark.asyncio
async def test_agent_consequential_confirmation():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"message": "Send an email to manager@corp.com saying Report is ready"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "ready to send" in data["display_text"].lower() or "should i send" in data["display_text"].lower()
