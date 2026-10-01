import streamlit as st

from src.mock_report import generate_mock_report
from src.models import ResearchReport


def show_report(report: ResearchReport) -> None:
    st.subheader("Research Report")
    st.info("이 리포트의 내용과 Sources는 고정된 Mock 예시이며 실제 조사 결과가 아닙니다.")

    st.header("Research Topic")
    st.write(report.topic)

    sections = (
        ("Requirements Summary", report.requirements_summary),
        ("Candidate Approaches", report.approaches),
        ("Comparison", report.comparison),
        ("Key Risks", report.risks),
        ("Implementation Checklist", report.checklist),
        ("Sources", report.sources),
    )
    for title, items in sections:
        st.header(title)
        for item in items:
            st.write(f"- {item}")


def main() -> None:
    st.set_page_config(page_title="Engineering Research Agent")
    st.title("Engineering Research Agent")
    st.write(
        "큰 기능을 구현하기 전에 조사 주제와 검토 항목을 정리하는 "
        "Research Report의 입력 → 출력 흐름을 확인하는 데모입니다."
    )
    st.warning("v0.1 Mock Demo — AI 및 Web Search는 아직 연결되지 않았습니다.")

    topic = st.text_area("기술 조사 주제", placeholder="예: 파일 업로드 기능 설계")
    st.caption("예시 주제: 파일 업로드 기능 설계, 알림 시스템 구현 방식 비교")

    if st.button("Generate Research Report"):
        if not topic.strip():
            st.warning("기술 조사 주제를 입력해 주세요.")
        else:
            show_report(generate_mock_report(topic))


if __name__ == "__main__":
    main()
