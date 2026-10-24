from src.markdown_export import report_to_markdown
from src.mock_report import generate_mock_report
from src.models import ApproachDetail, CommercialExample, ResearchPlan, ResearchReport, Source


def report_with_research() -> ResearchReport:
    return ResearchReport(
        topic="  파일 업로드 방식 비교  ",
        requirements_summary=["대용량 파일 지원", "권한 확인"],
        approaches=["서버 직접 업로드", "S3 Presigned URL"],
        comparison=["트래픽 비용 비교"],
        recommended_direction="Presigned URL부터 검토",
        risks=["만료 시간 관리"],
        checklist=["용량 제한 테스트"],
        sources=["https://invented.example/not-a-source"],
        source_details=[
            Source("AWS 문서", "https://docs.aws.amazon.com/example", cited=True),
            Source("Spring 가이드", "https://spring.io/guides/example"),
        ],
        research_plan=ResearchPlan(
            goal="업로드 방식 선택",
            key_questions=["성능 차이는?", "보안 조건은?"],
            perspectives=["운영", "비용"],
            search_query="file upload official docs",
        ),
        search_queries=["file upload official docs", "presigned URL security docs"],
        provider="Claude (Anthropic)",
        executive_summary=["결정은 신뢰 경계에 좌우된다.", "대용량은 직접 전송이 유리하다."],
        technical_scope=["클라이언트-저장소 전송 경로", "인증된 사용자"],
        decision_criteria=["지연 시간", "권한 경계", "운영 비용"],
        approach_details=[
            ApproachDetail(name="Presigned URL", architecture="클라이언트가 객체 저장소에 직접 전송한다.",
                           best_fit="대용량", strengths=["수평 확장"], tradeoffs=["만료 정책"],
                           implementation_steps=["서명 URL 발급 API 구현", "업로드 후 완료 검증"]),
        ],
        implementation_plan=["위협 모델 정의", "전송 경로 구현", "관측성 추가"],
        validation_plan=["부하 테스트", "권한 테스트", "복구 테스트"],
        evidence_limitations=["실제 워크로드 측정이 필요하다."],
        commercial_examples=[CommercialExample(
            product="Example Upload", observed_features="업로드 API", disclosed_implementation="내부 구현 비공개/미확인",
            implementation_takeaway="완료 검증 구현", evidence_status="not_disclosed",
            source_urls=["https://docs.aws.amazon.com/example"],
        )],
    )


def test_markdown_contains_every_report_section_and_search_history():
    markdown = report_to_markdown(report_with_research())

    for heading in (
        "조사 결과 · 구현 방식 요약", "상용 프로그램 사례와 적용 설계",
        "Research Topic", "Research Plan", "Search Queries / Search Rounds",
        "Research Provider", "Executive Summary", "Technical Scope & Assumptions",
        "Decision Criteria", "Technical Approach Details", "Implementation Plan",
        "Validation Plan", "Evidence Limitations",
        "Requirements Summary", "Candidate Approaches", "Comparison",
        "Recommended Direction", "Key Risks", "Implementation Checklist", "Sources",
    ):
        assert f"## {heading}\n" in markdown
    assert "파일 업로드 방식 비교" in markdown
    assert "### 조사 목표\n\n업로드 방식 선택" in markdown
    assert "- 성능 차이는?" in markdown
    assert "- 검색 Round: 2" in markdown
    assert "- 추가 검색: 수행" in markdown
    assert "1. file upload official docs" in markdown
    assert "2. presigned URL security docs" in markdown
    assert "- Presigned URL부터 검토" in markdown
    assert "### Presigned URL" in markdown
    assert "Claude (Anthropic)" in markdown
    assert markdown.index("## 조사 결과 · 구현 방식 요약") < markdown.index("## Research Plan")
    assert "구현 방식에는 크게 Presigned URL 등이 있습니다." in markdown
    assert "1. 서명 URL 발급 API 구현" in markdown
    assert "내부 구현 비공개/미확인" in markdown
    assert "Example Upload" in markdown
    assert markdown.endswith("\n")


def test_sources_use_recorded_metadata_and_keep_citation_status():
    markdown = report_to_markdown(report_with_research())

    assert "<https://docs.aws.amazon.com/example> (인용됨)" in markdown
    assert "<https://spring.io/guides/example> (검색 참조)" in markdown
    assert "invented.example" not in markdown


def test_legacy_mock_report_exports_without_plan_or_search_rounds():
    markdown = report_to_markdown(generate_mock_report("알림 시스템"))

    assert "## Research Plan\n\n기록 없음" in markdown
    assert "- 검색 Round: 0" in markdown
    assert "Mock Source A" in markdown
    assert "## Sources" in markdown
