# tool-colling (Python)

기상청 단기예보(동네예보) 데이터를 조회하는 Python MCP 서버 예제입니다.  
`stdio` / Streamable HTTP 두 가지 전송 방식을 지원하고, 별도로 Anthropic `tools` 기반 에이전트 루프 예시도 포함합니다.

코드는 **`src/` 레이아웃**으로 정리되어 있습니다.

## 기능

- MCP Tool: `get_short_term_forecast`
  - 입력: `location`(예: `서울`, `강남`, `부산`), `date`(`YYYY-MM-DD` 또는 `YYYYMMDD`)
  - 출력: 해당 날짜의 시간대별 예보 슬롯(기온, 강수확률, 하늘상태 등)
- KST(Asia/Seoul) 기준 최신 발표시각(`base_date`, `base_time`) 자동 선택
- 지역명 -> 기상청 격자(`nx`, `ny`) 매핑 지원 (일부 주요 지역 내장)

## 요구 사항

- Python `>=3.10`
- 공공데이터포털 기상청(단기예보) 서비스키
- (선택) Anthropic API Key (`weather_mcp.apps.agent_loop` 실행 시)

## 설치

권장: 편집 가능 설치로 패키지를 등록합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

패키지를 설치하지 않고 실행만 하려면 의존성 설치 후 `PYTHONPATH=src`로 모듈 실행하면 됩니다.

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m weather_mcp.apps.stdio
```

(`requirements.txt`는 `pyproject.toml`과 동일 의존성을 유지합니다.)

## 환경 변수 설정

루트의 `env.example`을 참고해 `.env` 파일을 만드세요.

```bash
cp env.example .env
```

필수/주요 변수:

- `KMA_SERVICE_KEY`: 공공데이터포털에서 발급한 기상청 단기예보 서비스키
- `PORT`: HTTP MCP 포트 (기본값 `3000`)
- `MCP_HOST`: HTTP MCP 바인딩 호스트 (기본값 `127.0.0.1`)
- `ANTHROPIC_API_KEY`: Anthropic API 키 (에이전트 루프 사용 시)
- `ANTHROPIC_MODEL`: 기본 `claude-sonnet-4-20250514`

## 실행 방법

`pip install -e .` 이후에는 콘솔 스크립트를 쓸 수 있습니다.

### 1) stdio MCP 서버

```bash
weather-mcp-stdio
```

또는 모듈 실행(개발 시 `pip install -e .` 없이):

```bash
PYTHONPATH=src python -m weather_mcp.apps.stdio
```

### 2) HTTP MCP 서버

```bash
weather-mcp-http
```

또는:

```bash
PYTHONPATH=src python -m weather_mcp.apps.http
```

엔드포인트(기본값):

- `http://127.0.0.1:3000/mcp`

### 3) Anthropic tools 루프 (MCP 없이)

```bash
weather-agent-loop "내일 강남 날씨 요약해줘"
```

또는:

```bash
PYTHONPATH=src python -m weather_mcp.apps.agent_loop "내일 강남 날씨 요약해줘"
```

## Cursor MCP 설정 예시

`cursor-mcp.example.json`은 `PYTHONPATH`에 `src`를 넣고 `python -m weather_mcp.apps.stdio`로 실행합니다.  
이미 `pip install -e .` 한 환경이라면 `PYTHONPATH` 없이 `weather-mcp-stdio`만 써도 됩니다.

## 프로젝트 구조

```text
src/weather_mcp/
  __init__.py
  server.py              # MCP 서버 / 툴 등록
  kma_client.py          # 기상청 API 호출·응답 가공
  grid.py                # 지역명 -> 격자 좌표
  apps/
    __init__.py
    stdio.py             # stdio MCP 진입점
    http.py              # Streamable HTTP MCP 진입점
    agent_loop.py        # Anthropic tools 루프 예제
pyproject.toml           # 패키지 메타·의존성·콘솔 스크립트
requirements.txt
env.example
cursor-mcp.example.json
README.md
```

## 참고 사항

- 지역 매핑에 없는 지역명은 기본값(서울 종로구 근처 격자)을 사용합니다.
- `date` 형식이 올바르지 않으면 에러를 반환합니다.
- 기상청 API `resultCode`가 `00`이 아닌 경우 에러로 처리합니다.
# korea-weather-mcp
