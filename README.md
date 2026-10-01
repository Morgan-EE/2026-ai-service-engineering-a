# Engineering Research Agent

개발 기능을 설계하기 전에 기술 선택지와 구현 위험을 조사하는 Streamlit 앱입니다. 사용자가 주제를 입력하면 조사 계획을 세우고, OpenAI Web Search로 자료를 찾은 뒤 근거의 충분성을 평가합니다. 필요한 경우에만 한 번 더 검색하여 출처가 포함된 Research Report를 만듭니다. 결과는 화면에서 읽거나 Markdown 파일로 다운로드할 수 있습니다.

## Current Status: v0.4 Report Export

v0.4는 v0.3의 bounded Research Loop와 보고서 구조를 유지하면서 Markdown 내보내기와 결과 화면을 개선했습니다. 실제 OpenAI API E2E 검증은 기능 구현 완료 후 별도로 수행할 예정입니다. 현재 검증은 mock 기반 단위 테스트와 로컬 Streamlit 기동 확인에 한정됩니다.

## 실행 흐름

1. **Research Plan:** 조사 목표, 핵심 질문, 조사 관점, 초기 검색 Query를 Pydantic 구조로 생성합니다.
2. **1차 Web Search:** OpenAI Responses API의 `web_search`로 근거, source, citation 메타데이터를 받습니다.
3. **충분성 판단:** 핵심 질문을 다뤘는지 `sufficient`, `missing_points`, `follow_up_query`로 평가합니다.
4. **조건부 2차 검색:** 근거가 부족한 경우에만 추가 검색을 한 번 수행합니다.
5. **Research Report:** 검색 근거를 바탕으로 Pydantic 구조의 보고서 본문을 만들고 실제 API 출처를 별도로 붙입니다.

검색은 최대 2 Round이며 무제한 Agent Loop는 없습니다. 두 Round의 출처는 URL 기준으로 중복 제거하고 인용 여부를 보존합니다. Sources의 URL은 모델이 작성한 본문에서 추출하지 않고 API의 `url_citation` 또는 `web_search_call.action.sources` 메타데이터에서만 가져옵니다. 실제 출처가 없으면 최종 보고서를 생성하지 않습니다.

## 보고서와 Markdown 다운로드

화면과 다운로드 파일에는 다음 정보가 포함됩니다.

- Research Topic
- Research Plan: 조사 목표, 핵심 질문, 조사 관점, 초기 검색 방향
- Search Queries / Search Rounds: 실행된 검색 횟수, 각 Query, 추가 검색 여부
- Requirements Summary
- Candidate Approaches
- Comparison
- Recommended Direction
- Key Risks
- Implementation Checklist
- Sources: API가 반환한 실제 URL과 인용 여부

조사가 끝나면 **Markdown 다운로드** 버튼으로 `engineering-research-report.md`를 저장할 수 있습니다. 앱은 세션 동안 마지막 결과를 유지하므로 화면을 다시 그리거나 다운로드 버튼을 눌러도 보고서가 사라지지 않습니다. 검색 근거의 클릭 가능한 인라인 인용은 화면의 별도 펼침 영역에서 확인할 수 있습니다.

## 설치 및 실행

Python 3.12 이상이 필요합니다. 저장소 루트에서 실행합니다.

```bash
python -m venv .venv
```

가상 환경 활성화: Windows PowerShell은 `.venv\Scripts\Activate.ps1`, macOS/Linux는 `source .venv/bin/activate`를 사용합니다. 활성화 후 의존성을 설치합니다.

```bash
python -m pip install -r requirements.txt
```

다음 환경변수를 설정하고 앱을 시작합니다.

```powershell
$env:OPENAI_API_KEY = "YOUR_KEY"
streamlit run app.py
```

`OPENAI_API_KEY`는 필수이며 코드에 하드코딩하지 않습니다. 선택적인 `OPENAI_MODEL`의 기본값은 `gpt-4.1-mini`입니다. [.env.example](.env.example)은 변수 예시이며 앱은 `.env`를 자동 로드하지 않습니다. `.env` 파일은 Git에서 제외됩니다. 빈 주제나 키 누락 시 API 호출 없이 안내 메시지를 표시합니다.

## 실행 제한과 오류 처리

- `MAX_SEARCH_ROUNDS = 2`, Round당 `MAX_TOOL_CALLS_PER_ROUND = 1`
- 모델 호출 최대 5회: 계획, 1차 검색, 충분성 평가, 조건부 2차 검색, 보고서
- SDK 자동 재시도 0회, API 호출당 timeout 45초
- 검색 실패, API 오류, 구조화 실패, 최종 출처 누락 시 오류 안내

## 프로젝트 구성

| 파일 | 역할 |
| --- | --- |
| `app.py` | 입력, 진행 상태, 보고서 및 다운로드 UI |
| `src/models.py` | Research Plan, Source, Research Report 모델 |
| `src/web_research.py` | 제한된 조사 흐름과 API 출처 수집 |
| `src/markdown_export.py` | 보고서를 Markdown으로 변환하는 순수 함수 |
| `src/mock_report.py` | v0.1 예제 및 회귀 테스트용 Mock |
| `tests/` | Mock, 검색 분기, 출처 보존, Markdown 변환 테스트 |

## 테스트

```bash
python -m pytest -q
python -m compileall -q app.py src tests
```

단위 테스트는 외부 OpenAI API를 호출하지 않습니다. 실제 API E2E 검증은 최종 단계에서 별도로 수행합니다.

## 버전 변화와 향후 계획

- **v0.1:** 고정 Mock Report로 입력·출력 흐름 확인
- **v0.2:** 실제 Web Search와 구조화된 Report, API citation/source 보존
- **v0.3:** Research Plan, 충분성 판단, 최대 2회 검색
- **v0.4:** Markdown 다운로드, 결과 화면과 상태 표시 개선

현재 범위에는 Multi-Agent, RAG, MCP, Reviewer Agent, DB 저장, 로그인, 별도 백엔드 서버, 배포가 포함되지 않습니다. 다음 단계에서는 실제 API E2E 검증과 출처 품질 및 보고서 주장·근거 대조를 검토합니다.
