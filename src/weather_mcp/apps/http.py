"""MCP Streamable HTTP transport entry."""

import os

from dotenv import load_dotenv

from weather_mcp.server import create_weather_mcp_server


def main() -> None:
    load_dotenv()
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "3000"))
    server = create_weather_mcp_server()
    server.run(transport="streamable-http", host=host, port=port, path="/mcp")


if __name__ == "__main__":
    main()
