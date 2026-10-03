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
