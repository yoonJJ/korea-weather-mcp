"""Anthropic Messages API tool loop (no MCP)."""

import json
import os
import sys

import requests
from dotenv import load_dotenv

from weather_mcp.kma_client import fetch_vilage_forecast

API = "https://api.anthropic.com/v1/messages"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

WEATHER_TOOL = {
    "name": "get_short_term_forecast",
    "description": (
        "기상청 단기예보(동네예보) 조회. "
        "지역명과 날짜로 기온·강수확률·하늘상태 등 예보를 가져옵니다."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": '조회 지역(한글), 예: "서울", "강남", "부산"',
            },
            "date": {
                "type": "string",
                "description": '예보를 묶어 볼 날짜. "YYYY-MM-DD" 또는 "YYYYMMDD"',
            },
        },
        "required": ["location", "date"],
    },
}


def call_anthropic(messages: list[dict]) -> dict:
    key = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY가 없습니다.")

    res = requests.post(
        API,
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": MODEL,
            "max_tokens": 2048,
            "tools": [WEATHER_TOOL],
            "messages": messages,
        },
        timeout=30,
    )
    data = res.json() if res.content else {}
    if res.status_code >= 400:
        err = ((data or {}).get("error") or {}).get("message") or json.dumps(data)
        raise RuntimeError(f"Anthropic {res.status_code}: {err}")
    return data


def run_tool(name: str, tool_input: dict) -> str:
    if name != "get_short_term_forecast":
        return json.dumps({"error": f"unknown tool: {name}"}, ensure_ascii=False)
    try:
        out = fetch_vilage_forecast(
            service_key=(os.getenv("KMA_SERVICE_KEY") or "").strip(),
            location=tool_input.get("location", ""),
            date=tool_input.get("date", ""),
        )
        return json.dumps(out, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def agent_loop(user_text: str) -> dict:
    messages: list[dict] = [{"role": "user", "content": user_text}]

    while True:
        msg = call_anthropic(messages)
        blocks = msg.get("content", [])
        messages.append({"role": "assistant", "content": blocks})

        if msg.get("stop_reason") != "tool_use":
            return {"final": msg, "messages": messages}

        tool_results = []
        for block in blocks:
            if block.get("type") != "tool_use":
                continue
            text = run_tool(block.get("name", ""), block.get("input", {}))
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id"),
                    "content": text,
                }
            )

        if not tool_results:
            return {"final": msg, "messages": messages}

        messages.append({"role": "user", "content": tool_results})


def main() -> None:
    load_dotenv()
    q = " ".join(sys.argv[1:]).strip() or "오늘 서울 날씨 요약해 줘."
    result = agent_loop(q)
    final = result["final"]
    text = "\n".join(
        block.get("text", "")
        for block in final.get("content", [])
        if block.get("type") == "text"
    )
    print(text or json.dumps(final, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
