"""KMA village forecast client."""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import requests

from weather_mcp.grid import resolve_grid

VILAGE_URL = (
    "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
)

ISSUE_ORDER = ["2300", "2000", "1700", "1400", "1100", "0800", "0500", "0200"]

CAT_LABEL = {
    "POP": "강수확률(%)",
    "PTY": "강수형태코드",
    "REH": "습도(%)",
    "SKY": "하늘상태코드",
    "TMP": "기온(℃)",
    "TMN": "최저기온(℃)",
    "TMX": "최고기온(℃)",
    "PCP": "1시간강수(mm)",
    "SNO": "1시간신적설(cm)",
    "VEC": "풍향(deg)",
    "WSD": "풍속(m/s)",
    "WAV": "파고(m)",
    "UUU": "풍속U(m/s)",
    "VVV": "풍속V(m/s)",
}


def pick_latest_issue_time(reference: dt.datetime | None = None) -> tuple[str, str]:
    kst = ZoneInfo("Asia/Seoul")
    now = reference.astimezone(kst) if reference else dt.datetime.now(tz=kst)

    for day_back in range(2):
        d = now - dt.timedelta(days=day_back)
        base_date = d.strftime("%Y%m%d")
        for bt in ISSUE_ORDER:
            hour = int(bt[:2])
            issue = d.replace(hour=hour, minute=0, second=0, microsecond=0)
            if issue <= now:
                return base_date, bt

    d = now - dt.timedelta(days=1)
    return d.strftime("%Y%m%d"), "2300"


def normalize_date_input(date_str: str) -> str | None:
    s = str(date_str or "").strip()
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        yyyy, mm, dd = s.split("-")
        if yyyy.isdigit() and mm.isdigit() and dd.isdigit():
            return s
    return None


def to_fcst_filter_ymd(iso_date: str) -> str:
    return iso_date.replace("-", "")


def fetch_vilage_forecast(*, service_key: str, location: str, date: str) -> dict:
    if not service_key:
        raise ValueError("KMA_SERVICE_KEY(또는 service_key)가 없습니다.")

    normalized = normalize_date_input(date)
    if not normalized:
        raise ValueError('date는 "YYYY-MM-DD" 또는 "YYYYMMDD" 형식이어야 합니다.')
    fcst_ymd = to_fcst_filter_ymd(normalized)

    grid = resolve_grid(location)
    nx, ny, matched = grid["nx"], grid["ny"], grid["matched"]
    base_date, base_time = pick_latest_issue_time()

    params = {
        "serviceKey": service_key,
        "pageNo": "1",
        "numOfRows": "1000",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": str(nx),
        "ny": str(ny),
    }
    response = requests.get(VILAGE_URL, params=params, timeout=15)
    if response.status_code >= 400:
        raise RuntimeError(f"기상청 HTTP {response.status_code}")

    data = response.json()
    header = ((data or {}).get("response") or {}).get("header") or {}
    result_code = header.get("resultCode")
    if result_code and result_code != "00":
        raise RuntimeError(f"기상청 API 오류: {header.get('resultMsg') or result_code}")

    body = ((data or {}).get("response") or {}).get("body") or {}
    items = (body.get("items") or {}).get("item")
    if isinstance(items, list):
        item_list = items
    elif items:
        item_list = [items]
    else:
        item_list = []

    filtered = [it for it in item_list if str(it.get("fcstDate")) == fcst_ymd]
    by_time: dict[str, dict] = {}
    for it in filtered:
        key = f"{it.get('fcstDate')}_{it.get('fcstTime')}"
        if key not in by_time:
            by_time[key] = {}
        label = CAT_LABEL.get(it.get("category"), it.get("category"))
        by_time[key][label] = it.get("fcstValue")

    slots = [
        {"fcstDateTime": k.replace("_", " "), **v}
        for k, v in sorted(by_time.items(), key=lambda x: x[0])
    ]

    return {
        "query": {
            "location": location,
            "gridMatch": matched,
            "nx": nx,
            "ny": ny,
            "requestedDate": normalized,
            "bulletin": {"base_date": base_date, "base_time": base_time},
        },
        "slots": slots,
        "rawItemCount": len(item_list),
        "filteredCount": len(filtered),
    }
