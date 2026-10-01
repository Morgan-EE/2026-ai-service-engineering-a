from html import escape

from src.markdown_export import report_to_markdown
from src.models import ResearchReport
from src.web_research import MAX_SEARCH_ROUNDS, ResearchError, generate_research_report


def evidence_html(report: ResearchReport) -> str:
    """Render API citation spans as clickable links without trusting model HTML."""
    text = report.search_evidence
    parts: list[str] = []
    position = 0
    for start, end, title, url in sorted(report.citation_spans):
        if not (position <= start < end <= len(text)):
            continue
        parts.append(escape(text[position:start]))
        parts.append(f'<a href="{escape(url, quote=True)}">{escape(title)}</a>')
        position = end
    parts.append(escape(text[position:]))
    return "".join(parts).replace("\n", "<br>")


def show_report(report: ResearchReport) -> None:
    import streamlit as st

    st.subheader("Research Report")
    st.caption("조사 결과와 API에서 제공한 출처를 함께 확인하세요.")
    st.download_button(
        "Markdown 다운로드",
        data=report_to_markdown(report).encode("utf-8"),
        file_name="engineering-research-report.md",
        mime="text/markdown",
        key="download_markdown",
    )

    st.header("Research Topic")
    st.write(report.topic)

    if report.research_plan is not None:
        with st.expander("Research Plan", expanded=True):
            st.markdown("**조사 목표**")
            st.write(report.research_plan.goal)
            questions, perspectives = st.columns(2)
            with questions:
                st.markdown("**핵심 질문**")
                for question in report.research_plan.key_questions:
                    st.write(f"- {question}")
            with perspectives:
                st.markdown("**조사 관점**")
                for perspective in report.research_plan.perspectives:
                    st.write(f"- {perspective}")
            st.caption(f"초기 검색 방향: {report.research_plan.search_query}")

    if report.search_queries:
        with st.expander("Search Rounds & Queries", expanded=True):
            st.write(f"검색 Round: {len(report.search_queries)} / {MAX_SEARCH_ROUNDS}")
            st.write("추가 검색: 수행" if len(report.search_queries) > 1 else "추가 검색: 없음")
            for index, query in enumerate(report.search_queries, start=1):
                st.markdown(f"**{index}차 검색 Query**")
                st.write(query)

    st.divider()

    sections = (
        ("Requirements Summary", report.requirements_summary),
        ("Candidate Approaches", report.approaches),
        ("Comparison", report.comparison),
        ("Recommended Direction", [report.recommended_direction]),
        ("Key Risks", report.risks),
        ("Implementation Checklist", report.checklist),
    )
    for title, items in sections:
        st.subheader(title)
        for item in items:
            st.write(f"- {item}")

    st.subheader("Sources")
    st.caption("아래 URL은 OpenAI Web Search가 반환한 citation/source 메타데이터에서 가져왔습니다.")
    for source in report.source_details:
        st.link_button(source.title, source.url)
        st.caption(f"{source.url} · {'인용됨' if source.cited else '검색 참조'}")

    with st.expander("검색 근거와 인라인 인용"):
        st.markdown(evidence_html(report), unsafe_allow_html=True)


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Engineering Research Agent", layout="wide")
    st.title("Engineering Research Agent")
    st.write(
        "개발 기술 조사 주제를 입력하면 실제 Web Search와 LLM 분석으로 "
        "출처가 포함된 Research Report를 생성합니다."
    )
    topic = st.text_area("기술 조사 주제", placeholder="예: 파일 업로드 기능 설계")
    st.caption("예시 주제: 파일 업로드 기능 설계, 알림 시스템 구현 방식 비교")

    submitted = st.button("Generate Research Report", type="primary")
    if submitted:
        if not topic.strip():
            st.warning("기술 조사 주제를 입력해 주세요.")
        else:
            st.session_state.pop("latest_report", None)
            report: ResearchReport | None = None
            with st.status("조사 계획 수립 중...", expanded=True) as status:
                def on_progress(stage: str, round_number: int, detail: str) -> None:
                    if stage == "plan_ready":
                        st.write(f"조사 계획 생성 · 초기 검색 방향: {detail}")
                    elif stage == "search_start":
                        status.update(label=f"{round_number}차 Web Search 진행 중...")
                        st.write(f"{round_number}차 검색 Query: {detail}")
                    elif stage == "search_complete":
                        st.write(f"{round_number}차 검색 완료 · {detail}")
                    elif stage == "assessment_start":
                        status.update(label="1차 검색 충분성 평가 중...")
                    elif stage == "assessment_complete":
                        st.write(f"1차 검색 평가: {detail}")
                    elif stage == "report_start":
                        status.update(label="최종 보고서 작성 중...")

                try:
                    report = generate_research_report(topic, on_progress=on_progress)
                except ResearchError as exc:
                    status.update(label="조사 오류", state="error")
                    st.error(f"조사 오류 · {exc}")
                else:
                    status.update(label="조사 완료", state="complete")
            if report is not None:
                st.session_state["latest_report"] = report
                st.success("조사 완료 · 실제 출처를 확인해 주세요.")

    saved_report = st.session_state.get("latest_report")
    if saved_report is not None:
        if not submitted or not topic.strip():
            st.caption("마지막 조사 결과")
        show_report(saved_report)
    elif not submitted:
        st.info("조사 대기 · 주제를 입력하고 보고서 생성을 누르세요.")


if __name__ == "__main__":
    main()
