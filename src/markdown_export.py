"""Convert a ResearchReport into a portable Markdown document."""

from src.models import ResearchReport


def _plain(text: str) -> str:
    return " ".join(text.split())


def _bullets(items: list[str]) -> str:
    lines = [f"- {_plain(item)}" for item in items if item.strip()]
    return "\n".join(lines) if lines else "- 기록 없음"


def report_to_markdown(report: ResearchReport) -> str:
    """Use report text for analysis and recorded source metadata for Sources."""
    lines = [
        "# Engineering Research Report",
        "",
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

    for title, items in (
        ("Requirements Summary", report.requirements_summary),
        ("Candidate Approaches", report.approaches),
        ("Comparison", report.comparison),
        ("Recommended Direction", [report.recommended_direction]),
        ("Key Risks", report.risks),
        ("Implementation Checklist", report.checklist),
    ):
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
