from types import SimpleNamespace as Obj
from unittest.mock import Mock

import pytest
from openai import OpenAIError

from src.models import ResearchReport
from src.web_research import ReportSections, ResearchError, generate_research_report
from app import evidence_html


def search_response():
    return Obj(
        status="completed",
        output_text="공식 문서에 따르면 방식 A를 검토할 수 있습니다. 인용",
        output=[
            Obj(type="web_search_call", status="completed", action=Obj(
                sources=[Obj(title="Official docs", url="https://example.com/docs")]
            )),
            Obj(type="message", content=[Obj(annotations=[Obj(
                type="url_citation", title="Official docs", url="https://example.com/docs",
                start_index=28, end_index=30,
            )])]),
        ],
    )


def sections_response():
    return Obj(status="completed", output_parsed=ReportSections(
        requirements_summary=["업로드 크기 확인"],
        approaches=["서버 직접 업로드", "Presigned URL"],
        comparison=["전송 비용과 운영 부담 비교"],
        recommended_direction="파일 크기에 따라 선택",
        risks=["권한 검증"],
        checklist=["최대 크기 테스트"],
    ))


def test_report_keeps_topic_and_api_citations():
    client = Obj(responses=Obj(create=Mock(return_value=search_response()),
                               parse=Mock(return_value=sections_response())))

    report = generate_research_report("  파일 업로드 설계  ", client=client)

    assert isinstance(report, ResearchReport)
    assert report.topic == "파일 업로드 설계"
    assert report.approaches == ["서버 직접 업로드", "Presigned URL"]
    assert report.recommended_direction == "파일 크기에 따라 선택"
    assert report.sources == ["https://example.com/docs"]
    assert report.source_details[0].cited
    assert report.citation_spans == [(28, 30, "Official docs", "https://example.com/docs")]
    assert client.responses.create.call_args.kwargs["tool_choice"] == "required"
    assert client.responses.create.call_args.kwargs["max_tool_calls"] == 2
    assert client.responses.parse.call_count == 1


def test_blank_topic_does_not_call_api():
    client = Obj(responses=Obj(create=Mock(), parse=Mock()))
    with pytest.raises(ValueError, match="must not be empty"):
        generate_research_report(" \n ", client=client)
    client.responses.create.assert_not_called()


def test_missing_key_fails_before_api_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ResearchError, match="OPENAI_API_KEY"):
        generate_research_report("업로드 설계")


def test_api_error_is_wrapped_without_retry():
    client = Obj(responses=Obj(create=Mock(side_effect=OpenAIError("failure")), parse=Mock()))
    with pytest.raises(ResearchError, match="OpenAI API"):
        generate_research_report("업로드 설계", client=client)
    assert client.responses.create.call_count == 1
    client.responses.parse.assert_not_called()


def test_no_verified_source_does_not_generate_report():
    response = search_response()
    response.output[0].action.sources = []
    response.output[1].content[0].annotations = []
    client = Obj(responses=Obj(create=Mock(return_value=response), parse=Mock()))
    with pytest.raises(ResearchError, match="실제 출처"):
        generate_research_report("업로드 설계", client=client)
    client.responses.parse.assert_not_called()


def test_model_backwards_compatible():
    report = ResearchReport("topic", ["r"], ["a"], ["c"], ["risk"], ["check"], ["mock"])
    assert report.recommended_direction == ""
    assert report.sources == ["mock"]


def test_evidence_citation_is_clickable_and_text_is_escaped():
    report = ResearchReport("topic", [], [], [], [], [], [],
                            search_evidence="<script> ref",
                            citation_spans=[(9, 12, "Official docs", "https://example.com/docs")])
    html = evidence_html(report)
    assert "&lt;script&gt;" in html
    assert '<a href="https://example.com/docs">Official docs</a>' in html
