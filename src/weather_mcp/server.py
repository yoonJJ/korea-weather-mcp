"""MCP server factory."""

import os

from mcp.server.fastmcp import FastMCP

from weather_mcp.kma_client import fetch_vilage_forecast


def create_weather_mcp_server() -> FastMCP:
    mcp = FastMCP(name="weather-mcp")

    @mcp.tool(
        name="get_short_term_forecast",
        description=(
            "기상청 단기예보(동네예보) 조회. "
            "지역명과 날짜로 기온·강수확률·하늘상태 등 예보를 가져옵니다."
        ),
    )
    def get_short_term_forecast(location: str, date: str) -> dict:
        try:
            return fetch_vilage_forecast(
                service_key=(os.getenv("KMA_SERVICE_KEY") or "").strip(),
                location=location,
                date=date,
            )
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}

    return mcp
