# 2026-ai-service-engineering-a
AI 서비스 엔지니어링 트랙A

# Engineering Research Agent

## 프로젝트 개요

Engineering Research Agent는 소프트웨어 개발 과정에서 규모가 큰 기능을 구현하기 전에 필요한 기술 조사와 레퍼런스 탐색을 자동화하기 위한 AI Agent 프로젝트입니다.

사용자가 개발 요구사항이나 조사 주제를 입력하면 Agent가 조사 계획을 수립하고, 웹 검색을 통해 공식 문서와 기술 자료, 구현 사례를 수집합니다. 이후 수집한 정보를 비교·정리하여 구현 방법별 장단점, 권장 방향, 주요 위험 요소, 구현 전 확인사항 및 참고 출처가 포함된 기술 조사 리포트를 생성하는 것을 목표로 합니다.

개인 소프트웨어 프로젝트에서 신규 기능을 설계하기 전에 반복적으로 수행하는 선행 기술 조사 시간을 줄이고, 필요한 근거와 선택지를 체계적으로 정리하는 용도로 활용할 예정입니다.

## 주요 기능

- 개발 요구사항 및 기술 조사 주제 분석
- 구조화된 Research Plan 생성
- OpenAI Web Search를 활용한 기술 자료 수집
- 1차 검색 충분성 판단 및 필요한 경우에만 추가 검색 1회
- 공식 문서 및 구현 사례 정리
- 구현 방법별 장단점 비교
- 위험 요소 및 구현 전 확인사항 도출
- API citation/source 메타데이터에 근거한 출처 표시

## 기본 실행 흐름

사용자 입력 → Research Plan → 1차 Web Search → 핵심 질문에 대한 근거 충분성 판단 → 충분하면 Report / 부족하면 2차 Web Search → Structured Research Report와 출처 표시

## 개발 계획

v0.3은 최대 2회 검색으로 제한된 단일 Agent 흐름입니다. 무제한 Agent Loop는 사용하지 않습니다.

이후 다음 기능을 단계적으로 적용할 예정입니다.

- 출처 검증 및 공식 문서 우선 검색
- 검색 결과 품질 검증
- 필요 시 Reviewer 또는 Multi-Agent 구조 적용

## 활용 계획

실제 개인 소프트웨어 프로젝트에서 규모가 큰 신규 기능을 개발하기 전 기술 검토 단계에 활용할 예정입니다. 공개 저장소에는 특정 프로젝트의 내부 정보와 무관한 범용 Agent 구조와 예제를 작성합니다.

## Current Status: v0.3 Research Loop

현재 버전은 실제 OpenAI Web Search와 LLM 분석을 연결합니다. v0.1의 고정 Mock Report는 회귀 테스트와 예제로 남아 있지만 실행 UI에서는 사용하지 않습니다. v0.3은 Pydantic Research Plan에 조사 목표, 핵심 질문, 조사 관점, 초기 검색 Query를 담습니다. 1차 검색 후 구조화된 충분성 평가(`sufficient`, `missing_points`, `follow_up_query`)를 수행하고, 부족한 경우에만 추가 검색을 한 번 실행합니다.

실제 출처 URL은 모델이 작성한 보고서 문자열에서 추출하지 않고 각 Web Search 응답의 `url_citation` 및 `web_search_call.action.sources`에서만 가져옵니다. 두 검색의 출처는 URL 기준으로 중복 제거하며, 인용 여부도 보존합니다. 검색 근거의 인라인 인용은 클릭할 수 있습니다. 두 검색 후에도 실제 출처가 없으면 보고서를 생성하지 않습니다.

## 설치 및 실행

Python 3.12 이상이 필요합니다. 저장소 루트에서 다음 명령을 실행합니다.

```bash
python -m venv .venv
```

가상 환경을 활성화합니다.

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

실행 전에 `OPENAI_API_KEY` 환경변수를 설정해야 합니다. 키를 코드나 `.env` 파일로 커밋하지 마세요. 선택적으로 `OPENAI_MODEL`을 지정할 수 있으며 기본값은 `gpt-4.1-mini`입니다. 예시는 `.env.example`에 있습니다. 앱은 `.env`를 자동으로 읽지 않습니다.

PowerShell 예시:

```powershell
$env:OPENAI_API_KEY = "YOUR_KEY"
streamlit run app.py
```

브라우저에서 Streamlit이 안내하는 로컬 주소를 열고 주제를 입력한 뒤 **Generate Research Report**를 누릅니다. 계획, 검색 단계 및 Query, 검색 Round 수, 추가 검색 여부, 보고서와 Sources를 확인할 수 있습니다. 내부 Chain-of-Thought는 표시하지 않습니다.

Harness 제약: `MAX_SEARCH_ROUNDS = 2`, 검색 Round당 `MAX_TOOL_CALLS_PER_ROUND = 1`, 모델 호출 최대 5회(계획·검색 1·충분성 평가·조건부 검색 2·보고서), SDK 자동 재시도 0회, API 호출당 timeout 45초입니다. 빈 주제 또는 키 누락 시 API 요청 없이 안내가 표시됩니다. 테스트는 저장소 루트에서 `python -m pytest`로 실행합니다. 실제 API E2E 검증은 프로젝트 기능 구현 완료 후 별도로 수행할 예정입니다.

## Report 구조

- Research Topic (입력 주제 유지)
- Research Plan (조사 목표, 핵심 질문, 조사 관점, 초기 검색 Query)
- Search Rounds (실행 횟수, 사용한 Query, 추가 검색 여부)
- Requirements Summary
- Candidate Approaches
- Comparison
- Recommended Direction
- Key Risks
- Implementation Checklist
- Sources (실제 API citation/source URL)
- 검색 근거와 클릭 가능한 인라인 인용

## v0.2와 달라진 점

v0.2는 단일 Web Search 후 보고서를 생성했습니다. v0.3은 검색 전에 계획을 만들고, 1차 근거가 핵심 질문에 충분한지 평가하며, 부족한 경우에만 2차 검색을 수행합니다. 기존 Research Report 구조와 API 메타데이터 기반 Sources는 유지합니다.

## 아직 구현되지 않은 것

- Multi-Agent
- RAG
- MCP
- Reviewer Agent
- 독립적인 URL 내용 재검증 및 보고서의 각 문장과 출처 사이의 자동 대조

## 향후 계획

다음 버전에서는 출처 품질 평가, 보고서 주장과 근거의 자동 대조, 결과 저장 및 공유를 검토할 예정입니다. 실제 API E2E 검증은 프로젝트 기능 구현 완료 후 수행합니다.
