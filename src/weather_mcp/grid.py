"""Location to KMA grid mapping helpers."""

DEFAULT_GRID = {"nx": 60, "ny": 127}

GRID_BY_LOCATION = {
    "서울": DEFAULT_GRID,
    "종로": {"nx": 60, "ny": 127},
    "중구": {"nx": 60, "ny": 127},
    "강남": {"nx": 61, "ny": 126},
    "송파": {"nx": 62, "ny": 126},
    "마포": {"nx": 55, "ny": 127},
    "부산": {"nx": 98, "ny": 76},
    "해운대": {"nx": 99, "ny": 75},
    "대구": {"nx": 89, "ny": 90},
    "인천": {"nx": 55, "ny": 124},
    "광주": {"nx": 58, "ny": 74},
    "대전": {"nx": 67, "ny": 100},
    "울산": {"nx": 102, "ny": 84},
    "세종": {"nx": 66, "ny": 103},
    "수원": {"nx": 60, "ny": 121},
    "성남": {"nx": 63, "ny": 124},
    "고양": {"nx": 57, "ny": 128},
    "용인": {"nx": 62, "ny": 120},
    "청주": {"nx": 69, "ny": 107},
    "전주": {"nx": 63, "ny": 89},
    "창원": {"nx": 90, "ny": 77},
    "제주": {"nx": 52, "ny": 38},
    "강릉": {"nx": 92, "ny": 131},
}


def resolve_grid(location: str) -> dict:
    key = "".join(str(location or "").strip().split())
    if not key:
        return {**DEFAULT_GRID, "matched": None}

    if key in GRID_BY_LOCATION:
        return {**GRID_BY_LOCATION[key], "matched": key}

    for k in GRID_BY_LOCATION:
        if key in k or k in key:
            return {**GRID_BY_LOCATION[k], "matched": k}

    return {**DEFAULT_GRID, "matched": None}
