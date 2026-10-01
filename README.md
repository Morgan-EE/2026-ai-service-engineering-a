# 2026-ai-service-engineering-a
AI 서비스 엔지니어링 트랙A

# Engineering Research Agent

## 프로젝트 개요

Engineering Research Agent는 소프트웨어 개발 과정에서 규모가 큰 기능을 구현하기 전에 필요한 기술 조사와 레퍼런스 탐색을 자동화하기 위한 AI Agent 프로젝트입니다.

사용자가 개발 요구사항이나 조사 주제를 입력하면 Agent가 조사 계획을 수립하고, 웹 검색을 통해 공식 문서와 기술 자료, 구현 사례를 수집합니다. 이후 수집한 정보를 비교·정리하여 구현 방법별 장단점, 권장 방향, 주요 위험 요소, 구현 전 확인사항 및 참고 출처가 포함된 기술 조사 리포트를 생성하는 것을 목표로 합니다.

개인 소프트웨어 프로젝트에서 신규 기능을 설계하기 전에 반복적으로 수행하는 선행 기술 조사 시간을 줄이고, 필요한 근거와 선택지를 체계적으로 정리하는 용도로 활용할 예정입니다.

## 주요 기능

- 개발 요구사항 및 기술 조사 주제 분석
- 조사 계획 및 검색 Query 생성
- Web Search Tool을 활용한 기술 자료 수집
- 공식 문서 및 구현 사례 정리
- 구현 방법별 장단점 비교
- 위험 요소 및 구현 전 확인사항 도출
- 참고 출처가 포함된 Markdown 기술 리포트 생성

## 기본 실행 흐름

사용자 입력  
→ 조사 계획 수립  
→ 웹 검색  
→ 검색 결과 선별 및 분석  
→ 필요 시 추가 검색  
→ 기술 조사 리포트 생성

## 개발 계획

초기 버전에서는 단일 Agent와 Web Search Tool을 기반으로 핵심 기능을 구현합니다.

이후 다음 기능을 단계적으로 적용할 예정입니다.

- Structured Output을 활용한 결과 구조화
- 최대 검색 횟수 및 Agent Step 제한
- 출처 검증 및 공식 문서 우선 검색
- 검색 결과 품질 검증
- 필요 시 Reviewer 또는 Multi-Agent 구조 적용

## 활용 계획

실제 개인 소프트웨어 프로젝트에서 규모가 큰 신규 기능을 개발하기 전 기술 검토 단계에 활용할 예정입니다. 공개 저장소에는 특정 프로젝트의 내부 정보와 무관한 범용 Agent 구조와 예제를 작성합니다.

## Current Status: v0.1 Mock Demo

현재 버전은 실제 조사 Agent가 아닌 Input → Output UX 확인용 Mock Demo입니다. 생성되는 리포트의 모든 내용과 Sources는 고정된 예시 데이터입니다. AI 및 Web Search는 연결되어 있지 않습니다.

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

브라우저에서 Streamlit이 안내하는 로컬 주소를 열고 주제를 입력한 뒤 **Generate Research Report**를 누릅니다. 테스트는 저장소 루트에서 `python -m pytest`로 실행할 수 있습니다.

## Demo에서 가능한 것

- 기술 조사 주제 입력 및 빈 입력 안내
- 입력 주제가 포함된 결정적 Mock Research Report 생성
- 요구사항, 후보 접근법, 비교, 위험 요소, 체크리스트, Mock Sources 확인

## 아직 구현되지 않은 것

- LLM을 통한 주제 분석 및 보고서 생성
- Web Search 및 실제 출처 수집·검증
- 조사 계획, 재검색 등을 수행하는 Agent Loop

## 향후 계획

v0.2에서는 실제 자료 수집을 위한 Web Search Agent 연동 범위와 출처 검증 방식을 정의하고, 현재 구조화된 리포트 모델을 실제 조사 결과에 연결할 예정입니다. 이후 단계에서는 위의 개발 계획에 따라 Structured Output과 검색·Agent Step 제한 등을 검토합니다.
