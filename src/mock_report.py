from src.models import ResearchReport


def generate_mock_report(topic: str) -> ResearchReport:
    """Return the same illustrative report for the same non-empty topic."""
    topic = topic.strip()
    if not topic:
        raise ValueError("Research topic must not be empty")

    return ResearchReport(
        topic=topic,
        requirements_summary=[
            "필요한 입력, 기대 출력, 성공 기준을 정의합니다.",
            "성능, 보안, 운영 제약을 이해관계자와 확인합니다.",
        ],
        approaches=[
            "접근 A (예시): 검증된 기존 도구를 활용합니다.",
            "접근 B (예시): 필요한 범위만 직접 구현합니다.",
        ],
        comparison=[
            "개발 속도 (가정): 접근 A가 빠를 수 있으나 도입 조건을 확인해야 합니다.",
            "제어 범위 (가정): 접근 B가 넓을 수 있으나 유지보수 부담을 확인해야 합니다.",
        ],
        risks=[
            "현재 내용은 실제 자료로 검증되지 않은 예시입니다.",
            "보안, 비용, 운영 영향은 실제 요구사항에 맞춰 별도 평가가 필요합니다.",
        ],
        checklist=[
            "요구사항과 제약 조건을 구체화합니다.",
            "후보별 공식 문서와 구현 사례를 실제로 확인합니다.",
            "작은 실험으로 핵심 가정을 검증합니다.",
        ],
        sources=[
            "Mock Source A — 공식 문서 자리표시자 (실제 검색 결과 아님)",
            "Mock Source B — 구현 사례 자리표시자 (실제 검색 결과 아님)",
        ],
    )
