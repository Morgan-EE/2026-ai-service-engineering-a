"""Convert a ResearchReport into a portable Markdown document."""

from src.models import ResearchReport


def _plain(text: str) -> str:
    return " ".join(text.split())


def _bullets(items: list[str]) -> str:
    lines = [f"- {_plain(item)}" for item in items if item.strip()]
    return "\n".join(lines) if lines else "- 기록 없음"


def result_summary_markdown(report: ResearchReport) -> str:
    names = [item.name for item in report.approach_details] or report.approaches
    lines = ["구현 방식에는 크게 " + ", ".join(_plain(name) for name in names) + " 등이 있습니다.", ""]
    for approach in report.approach_details:
        lines.extend([f"### {_plain(approach.name)}", "",
                      "이 방식은 다음 순서와 처리 흐름으로 구현할 수 있습니다.", "",
                      f"처리 흐름: {_plain(approach.architecture)}", ""])
        steps = getattr(approach, "implementation_steps", [])
        lines.extend(f"{index}. {_plain(step)}" for index, step in enumerate(steps, 1))
        lines.extend(["", f"적합한 상황: {_plain(approach.best_fit)}", ""])
    if report.recommended_direction:
        lines.extend(["### 권장 시작점", "", _plain(report.recommended_direction), ""])
    return "\n".join(lines)


def commercial_examples_markdown(report: ResearchReport) -> str:
    cases = getattr(report, "commercial_examples", [])
    if not cases:
        return "공식 자료로 확인한 상용 사례가 없습니다. 추가 확인이 필요합니다."

    status_labels = {"documented": "기술 공개", "not_disclosed": "내부 구현 비공개/미확인", "unverified": "미확인"}
    def cell(text: str) -> str:
        return _plain(text).replace("|", "\\|")

    lines = [
        "공개 자료로 확인한 동작과 우리 서비스에 적용할 설계를 구분했습니다.", "",
        "| 상용 프로그램 | 확인된 기능·흐름 | 공개된 구현 방식 | 적용할 설계 (제안) | 근거 상태 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in cases:
        values = (case.product, case.observed_features, case.disclosed_implementation,
                  case.implementation_takeaway, status_labels[case.evidence_status])
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.append("")
    for case in cases:
        sources = " · ".join(f"<{url}>" for url in case.source_urls) or "확인된 출처 없음"
        lines.append(f"- {cell(case.product)} 근거: {sources}")
    return "\n".join(lines)


def report_to_markdown(report: ResearchReport) -> str:
    """Use report text for analysis and recorded source metadata for Sources."""
    lines = [
        "# Engineering Research Report",
        "",
        "## 조사 결과 · 구현 방식 요약", "", result_summary_markdown(report), "",
        "## 상용 프로그램 사례와 적용 설계", "", commercial_examples_markdown(report), "",
        "## Research Topic",
        "",
        _plain(report.topic),
        "",
        "## Research Plan",
        "",
    ]

    plan = report.research_plan
    if plan is None:
        lines.extend(["기록 없음", ""])
    else:
        lines.extend([
            "### 조사 목표", "", _plain(plan.goal), "",
            "### 핵심 질문", "", _bullets(plan.key_questions), "",
            "### 조사 관점", "", _bullets(plan.perspectives), "",
            "### 초기 검색 방향", "", _plain(plan.search_query), "",
        ])
        if getattr(plan, "commercial_search_query", ""):
            lines.extend(["### 상용 사례 검색 방향", "", _plain(plan.commercial_search_query), ""])

    lines.extend([
        "## Search Queries / Search Rounds", "",
        f"- 검색 Round: {len(report.search_queries)}",
        f"- 추가 검색: {'수행' if len(report.search_queries) > 1 else '없음'}",
        "",
    ])
    lines.extend(f"{index}. {_plain(query)}" for index, query in enumerate(report.search_queries, 1))
    if not report.search_queries:
        lines.append("기록 없음")
    lines.append("")

    if report.provider:
        lines.extend(["## Research Provider", "", _plain(report.provider), ""])

    for title, items in (
        ("Executive Summary", report.executive_summary),
        ("Technical Scope & Assumptions", report.technical_scope),
        ("Decision Criteria", report.decision_criteria),
    ):
        if items:
            lines.extend([f"## {title}", "", _bullets(items), ""])

    for title, items in (
        ("Requirements Summary", report.requirements_summary),
        ("Candidate Approaches", report.approaches),
        ("Comparison", report.comparison),
        ("Recommended Direction", [report.recommended_direction]),
        ("Key Risks", report.risks),
        ("Implementation Checklist", report.checklist),
    ):
        lines.extend([f"## {title}", "", _bullets(items), ""])

    if report.approach_details:
        lines.extend(["## Technical Approach Details", ""])
        for approach in report.approach_details:
            lines.extend([
                f"### {_plain(approach.name)}", "",
                f"- Architecture: {_plain(approach.architecture)}",
                f"- Best fit: {_plain(approach.best_fit)}",
                "- Strengths:",
                _bullets(approach.strengths),
                "- Trade-offs:",
                _bullets(approach.tradeoffs),
                "",
            ])

    for title, items in (
        ("Implementation Plan", report.implementation_plan),
        ("Validation Plan", report.validation_plan),
        ("Evidence Limitations", report.evidence_limitations),
    ):
        if items:
            lines.extend([f"## {title}", "", _bullets(items), ""])

    lines.extend(["## Sources", ""])
    if report.source_details:
        lines.extend(
            f"- {_plain(source.title)} — <{source.url}> "
            f"({'인용됨' if source.cited else '검색 참조'})"
            for source in report.source_details
        )
    else:
        source_lines = [f"- {_plain(source)}" for source in report.sources if source.strip()]
        lines.extend(source_lines or ["- 기록 없음"])
    lines.append("")
    return "\n".join(lines)
