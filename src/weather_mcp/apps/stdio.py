"""MCP stdio transport entry."""

from dotenv import load_dotenv

from weather_mcp.server import create_weather_mcp_server


def main() -> None:
    load_dotenv()
    server = create_weather_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
