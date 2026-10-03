# Engineering Research Agent

개발 기능을 설계하기 전에 기술 선택지와 구현 위험을 조사하는 AI 기반 기술 조사 Agent입니다.

사용자가 개발 요구사항이나 기술 조사 주제를 입력하면 Research Plan을 생성하고, OpenAI Web Search를 통해 실제 기술 자료를 수집합니다. 이후 검색 결과가 핵심 질문을 충분히 다루고 있는지 평가하고, 필요한 경우에만 추가 검색을 수행합니다.

수집한 근거를 바탕으로 구현 방법별 비교, 권장 방향, 주요 위험 요소, 구현 전 확인사항 및 실제 출처가 포함된 구조화된 Research Report를 생성합니다.

결과는 Streamlit 화면에서 확인하거나 Markdown 파일로 다운로드할 수 있습니다.

---

## Current Status: Final E2E Validated

Engineering Research Agent의 핵심 기능 구현과 실제 OpenAI API 기반 E2E 검증을 완료했습니다.

현재 Agent의 전체 흐름은 다음과 같습니다.

```text
사용자 조사 주제 입력
        ↓
Research Plan 생성
        ↓
1차 Web Search
        ↓
검색 결과 충분성 평가
        ↓
┌──────────────────────┐
│ 근거 충분            │ 근거 부족
│                      ↓
│               조건부 2차 Web Search
│                      │
└──────────────┬───────┘
               ↓
Structured Research Report
               ↓
Sources / Citation 표시
               ↓
Markdown 다운로드

검색은 최대 2 Round로 제한하며 무제한 Agent Loop를 사용하지 않습니다.
최종 실제 API E2E 검증에서는 Spring Boot 대용량 파일 업로드 기술 조사를 수행하여 다음 전체 흐름을 확인했습니다.
- Research Plan 생성
- 1차 Web Search
- 검색 결과 충분성 평가
- 조건부 2차 Web Search
- Structured Research Report 생성
- 실제 Sources 표시
- API url_citation 표시
- 클릭 가능한 인라인 citation
- Streamlit 화면 렌더링
- Markdown Report 다운로드
최종 E2E 검증 결과:
- Web Search: 2 / 2 Round 정상 수행
- 중복 제거된 실제 HTTP(S) Sources: 17개
- API url_citation: 3개
- pytest: 19개 통과
- Python compile/import 검사 통과
- Streamlit health endpoint: HTTP 200
- Markdown UTF-8 다운로드 및 보고서 섹션·Source URL 확인
실제 출처 URL은 모델이 작성한 본문에서 생성하거나 추출하지 않습니다.
OpenAI Web Search API가 반환한 url_citation 또는 web_search_call.action.sources 메타데이터에서만 수집합니다.
주요 기능
- 개발 기술 조사 주제 입력
- Research Plan 자동 생성
- 조사 목표 및 핵심 질문 정의
- OpenAI Responses API Web Search
- 검색 결과 충분성 평가
- 부족한 근거에 대한 조건부 추가 검색
- 최대 검색 Round 제한
- Pydantic Structured Output 기반 Report 생성
- 구현 방식별 비교
- Recommended Direction 생성
- 주요 위험 요소 및 구현 Checklist 제공
- 실제 API Source / Citation 표시
- Source URL 중복 제거
- 클릭 가능한 인라인 Citation
- Markdown Report 다운로드
- API 오류 및 출처 누락 처리
실행 흐름
1. Research Plan
사용자의 조사 주제를 바탕으로 다음 정보를 포함한 Research Plan을 생성합니다.
- 조사 목표
- 핵심 질문
- 조사 관점
- 초기 Search Query
Research Plan은 Pydantic Structured Output으로 관리합니다.
2. 1차 Web Search
OpenAI Responses API의 web_search Tool을 이용하여 실제 웹 자료를 조사합니다.
조사 시 공식 문서와 신뢰할 수 있는 기술 자료를 우선하도록 요청합니다.
Web Search 응답에서 다음 정보를 수집합니다.
- 검색 결과 Evidence
- url_citation
- web_search_call.action.sources
3. 충분성 평가
1차 검색 결과가 Research Plan의 핵심 질문을 충분히 다루는지 평가합니다.
평가 결과는 다음과 같이 구조화됩니다.
- sufficient
- missing_points
- follow_up_query
4. 조건부 2차 검색
1차 검색 결과가 충분하면 추가 검색 없이 Report 생성 단계로 이동합니다.
근거가 부족하거나 필요한 Citation이 확보되지 않은 경우에만 추가 검색을 한 번 수행합니다.
검색 Round는 최대 2회입니다.
5. Research Report
수집된 검색 Evidence를 기반으로 최종 Research Report를 생성합니다.
Report 본문은 Pydantic Structured Output을 이용하여 구조화합니다.
Research Report 구조
생성되는 Report에는 다음 정보가 포함됩니다.
Research Topic
사용자가 입력한 기술 조사 주제입니다.
Research Plan
- Goal
- Key Questions
- Perspectives
- Initial Search Query
Search History
- Search Round 수
- 각 Round에서 사용한 Query
- 추가 검색 여부
Requirements Summary
조사 주제의 주요 요구사항을 정리합니다.
Candidate Approaches
검토 가능한 구현 방식 또는 기술 선택지를 정리합니다.
Comparison
후보 방식들의 차이와 선택 기준을 비교합니다.
Recommended Direction
현재 조사 결과를 기준으로 권장할 수 있는 구현 방향을 정리합니다.
Key Risks
구현 과정에서 고려해야 할 주요 위험 요소를 정리합니다.
Implementation Checklist
실제 구현 전에 확인해야 할 항목을 제공합니다.
Sources
OpenAI Web Search API가 반환한 실제 Source URL과 Citation 정보를 표시합니다.
출처 처리 정책
Engineering Research Agent는 모델이 생성한 텍스트에서 URL을 추출하지 않습니다.
Sources는 다음 API 메타데이터에서만 수집합니다.
url_citation
web_search_call.action.sources

각 검색 Round의 출처는 URL을 기준으로 중복 제거합니다.
실제 Source 또는 Citation을 확인할 수 없는 경우 정상적인 Report로 처리하지 않습니다.
최종 E2E 검증 과정에서 Web Search Source는 존재하지만 인라인 Citation이 생성되지 않는 상황을 발견했고, 이를 보완했습니다.
현재는 Citation이 확보되지 않은 경우 검색 Round 상한 내에서 추가 검색을 수행하며, 최대 검색 이후에도 검증된 인라인 Citation이 없으면 Report 생성을 중단합니다.
Harness / 실행 제한
Agent의 무제한 실행과 불필요한 API 사용을 방지하기 위해 애플리케이션 수준에서 실행을 제한합니다.
MAX_SEARCH_ROUNDS = 2
MAX_TOOL_CALLS_PER_ROUND = 1
API_TIMEOUT_SECONDS = 45
SDK_MAX_RETRIES = 0

하나의 정상적인 조사 요청에서 수행될 수 있는 모델 단계는 최대 다음과 같습니다.
1. Research Plan 생성
2. 1차 Web Search
3. 충분성 평가
4. 조건부 2차 Web Search
5. Research Report 생성

다음 상황에서는 오류를 반환합니다.
- 빈 조사 주제
- API Key 누락
- OpenAI API 오류
- Research Plan 구조화 실패
- Web Search 실패
- 실제 Source 누락
- 최종 Citation 누락
- Structured Report 생성 실패
무제한 재시도 및 무제한 Agent Loop는 사용하지 않습니다.
Streamlit UI
Streamlit 화면에서는 다음 정보를 확인할 수 있습니다.
- 조사 대기 상태
- Research Plan 생성 상태
- Web Search 진행 상태
- 충분성 평가 상태
- 조건부 추가 검색 상태
- Report 생성 상태
- Research Plan
- Search Round
- Search Query
- 최종 Research Report
- Sources
- 검색 Evidence
- 클릭 가능한 인라인 Citation
- Markdown 다운로드
Agent 내부 Chain-of-Thought는 노출하지 않습니다.
Research Plan, Query, 검색 Round와 같이 사용자에게 공개 가능한 실행 정보만 표시합니다.
Markdown 다운로드
조사가 완료되면 Download Markdown Report 버튼을 이용하여 결과를 Markdown 파일로 저장할 수 있습니다.
기본 파일명:
engineering-research-report.md

Markdown Report에는 다음 내용이 포함됩니다.
- Research Topic
- Research Plan
- Search History
- Requirements Summary
- Candidate Approaches
- Comparison
- Recommended Direction
- Key Risks
- Implementation Checklist
- Sources
Sources에는 실제 API metadata에서 수집한 Source title과 URL이 포함됩니다.
최종 E2E 검증에서는 실제 조사 결과를 브라우저에서 Markdown 파일로 다운로드하고 UTF-8 내용 및 Report 섹션과 Source URL을 확인했습니다.
설치 및 실행
Python 3.12 이상이 필요합니다.
저장소를 Clone한 뒤 프로젝트 루트로 이동합니다.
git clone https://github.com/Morgan-EE/2026-ai-service-engineering-a.git
cd 2026-ai-service-engineering-a

가상 환경을 생성합니다.
python -m venv .venv

Windows PowerShell:
.venv\Scripts\Activate.ps1

macOS / Linux:
source .venv/bin/activate

의존성을 설치합니다.
python -m pip install -r requirements.txt

환경변수
OPENAI_API_KEY가 필요합니다.
Windows PowerShell:
$env:OPENAI_API_KEY = "YOUR_KEY"

선택적으로 사용할 모델을 지정할 수 있습니다.
$env:OPENAI_MODEL = "gpt-4.1-mini"

기본 모델:
gpt-4.1-mini

.env.example은 필요한 환경변수의 예시입니다.
실제 API Key는 코드에 하드코딩하지 않으며 .env 파일은 Git에서 제외됩니다.
실행
python -m streamlit run app.py

브라우저에서 Streamlit이 제공하는 로컬 주소에 접속합니다.
기술 조사 주제를 입력한 뒤 Generate Research Report 버튼을 누르면 조사가 시작됩니다.
예시:
Spring Boot 애플리케이션에서 대용량 파일 업로드를 구현할 때
서버 직접 업로드와 S3 Presigned URL 방식의 차이,
보안·비용·확장성 측면의 선택 기준을 조사해줘.

프로젝트 구성
파일	역할
app.py	사용자 입력, 진행 상태, Report 및 Markdown 다운로드 UI
src/models.py	Research Plan, Source, Research Report 모델
src/web_research.py	Research Plan, Web Search, 충분성 평가, 제한된 Agent Loop 및 출처 수집
src/markdown_export.py	Research Report를 Markdown으로 변환
src/mock_report.py	v0.1 예제 및 회귀 테스트용 Mock
tests/test_web_research.py	Web Search 분기, Agent Loop, Source/Citation 및 오류 처리 테스트
tests/test_markdown_export.py	Markdown 변환 및 파일명 처리 테스트
requirements.txt	Python 의존성
.env.example	환경변수 설정 예시


테스트
전체 단위 테스트:
python -m pytest -q

Python compile 검사:
python -m compileall -q app.py src tests

단위 테스트에서는 실제 OpenAI API를 호출하지 않고 Mock / Stub을 사용합니다.
현재 최종 테스트 결과:
19 passed

최종 통합 단계에서는 별도로 실제 OpenAI API 기반 E2E 검증도 수행했습니다.
실제 E2E 검증
최종 통합 검증에서는 다음 주제를 사용했습니다.
Spring Boot 애플리케이션에서 대용량 파일 업로드를 구현할 때
서버 직접 업로드와 S3 Presigned URL 방식의 차이,
보안·비용·확장성 측면의 선택 기준을 조사해줘.

검증 결과:
항목	결과
Research Plan	성공
1차 Web Search	성공
충분성 평가	성공
조건부 2차 Web Search	수행
Search Round	2 / 2
Structured Report	성공
실제 HTTP(S) Sources	17개
API url_citation	3개
Streamlit 렌더링	성공
인라인 Citation	성공
Markdown 다운로드	성공
UTF-8 Markdown 확인	성공
pytest	19 passed
compile/import	성공
Streamlit health	HTTP 200


Case 1에서 전체 Agent Flow가 검증되었기 때문에 추가 API 비용을 줄이기 위해 두 번째 E2E Case는 실행하지 않았습니다.
모든 Report 주장과 Source 사이의 일대일 자동 검증은 현재 범위에 포함하지 않습니다.
버전 히스토리
v0.1 - Mock Demo
- Streamlit 기본 UI
- 기술 조사 주제 입력
- 고정 Mock Research Report
- Report 구조 설계
v0.2 - Web Search + Structured Output
- 실제 OpenAI Web Search 연결
- Pydantic Structured Output
- 실제 Source / Citation metadata 수집
- Mock 기반 단위 테스트 추가
v0.3 - Bounded Research Agent Loop
- Research Plan 생성
- 검색 결과 충분성 평가
- 조건부 Follow-up Search
- 최대 2 Round 검색 제한
- Source 병합 및 중복 제거
- Harness 실행 제한 적용
v0.4 - Report Export + UX
- Markdown Report 생성
- Markdown 다운로드
- Research Plan / Search History UI 개선
- 진행 상태 및 오류 메시지 개선
- 결과 세션 유지
Final E2E Validation
- 실제 OpenAI API 기반 E2E 검증
- 실제 Sources 및 Citation 검증
- 인라인 Citation 누락 문제 발견 및 수정
- Citation 누락 회귀 테스트 추가
- 실제 Markdown 다운로드 검증
- 전체 pytest 19개 통과
Git 기반 개발 흐름
기능 개발은 Feature Branch와 Pull Request를 이용하여 관리했습니다.
main
 ├─ feat/v0.2-web-research
 ├─ feat/v0.3-research-loop
 ├─ feat/v0.4-report-export
 └─ fix/final-e2e-validation

각 단계에서 다음 흐름을 사용했습니다.
Feature / Fix
→ Branch
→ 구현
→ 테스트
→ Commit
→ Push
→ Pull Request
→ 검토
→ main Merge

최종 E2E 검증 중 발견된 문제 역시 별도의 Fix Branch와 Pull Request를 통해 수정했습니다.
현재 구현 범위
현재 버전에서 구현하지 않은 기능:
- Multi-Agent
- RAG
- MCP
- Reviewer Agent
- Vector DB
- 사용자 로그인
- 조사 결과 DB 저장
- 별도 Backend API
- 서비스 배포
- 모든 주장과 출처 간 자동 근거 대조
현재 프로젝트의 목표는 복잡한 기능을 모두 구현하는 것이 아니라, 실제 개발 기술 조사 과정에서 사용할 수 있는 작고 통제 가능한 Research Agent를 구현하는 것입니다.
향후 개선 방향
추가 개발 시 다음 기능을 검토할 수 있습니다.
- 공식 문서 우선순위 강화
- Source 신뢰도 및 품질 평가
- Report의 개별 주장과 Source 간 자동 근거 대조
- 검색 결과 품질 Score
- 조사 결과 저장 및 공유
- 동일 주제 Research History 관리
- 필요 시 Reviewer Agent 추가
현재 핵심 기능과 실제 OpenAI API 기반 E2E 검증까지 완료된 상태입니다.
