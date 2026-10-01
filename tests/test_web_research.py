from types import SimpleNamespace as Obj
from unittest.mock import Mock

import pytest
from openai import OpenAIError

from app import evidence_html
from src.models import ResearchPlan, ResearchReport
from src.web_research import (
    MAX_SEARCH_ROUNDS,
    MAX_TOOL_CALLS_PER_ROUND,
    ReportSections,
    ResearchError,
    SufficiencyAssessment,
    generate_research_report,
)


SOURCE_A = "https://example.com/docs"
SOURCE_B = "https://example.org/guide"


def parsed(value):
    return Obj(status="completed", output_parsed=value)


def plan_response():
    return parsed(ResearchPlan(
        goal="파일 업로드 방식 선택",
        key_questions=["성능 차이는?", "보안 조건은?"],
        perspectives=["비용", "운영"],
        search_query="file upload architecture official docs",
    ))


def assessment_response(sufficient: bool):
    return parsed(SufficiencyAssessment(
        sufficient=sufficient,
        missing_points=[] if sufficient else ["보안 조건"],
        follow_up_query=None if sufficient else "presigned URL security official docs",
    ))


def sections_response():
    return parsed(ReportSections(
        requirements_summary=["업로드 크기 확인"],
        approaches=["서버 직접 업로드", "Presigned URL"],
        comparison=["전송 비용과 운영 부담 비교"],
        recommended_direction="파일 크기에 따라 선택",
        risks=["권한 검증"],
        checklist=["최대 크기 테스트"],
    ))


def search_response(urls=(SOURCE_A,), cited_url=SOURCE_A, evidence="Evidence ref"):
    annotations = []
    if cited_url is not None:
        annotations.append(Obj(
            type="url_citation", title="Cited docs", url=cited_url,
            start_index=9, end_index=12,
        ))
    return Obj(
        status="completed",
        output_text=evidence,
        output=[
            Obj(type="web_search_call", status="completed", action=Obj(
                sources=[Obj(title="Official docs", url=url) for url in urls]
            )),
            Obj(type="message", content=[Obj(annotations=annotations)]),
        ],
    )


def client_for(searches, sufficient=True):
    return Obj(responses=Obj(
        create=Mock(side_effect=searches),
        parse=Mock(side_effect=[plan_response(), assessment_response(sufficient), sections_response()]),
    ))


def test_sufficient_first_round_skips_follow_up_and_keeps_topic_and_citation():
    client = client_for([search_response()])
    events = []

    report = generate_research_report("  파일 업로드 설계  ", client=client,
                                      on_progress=lambda *args: events.append(args))

    assert isinstance(report, ResearchReport)
    assert report.topic == "파일 업로드 설계"
    assert report.research_plan.goal == "파일 업로드 방식 선택"
    assert report.search_queries == ["file upload architecture official docs"]
    assert report.sources == [SOURCE_A]
    assert report.source_details[0].cited
    assert report.citation_spans == [(9, 12, "Cited docs", SOURCE_A)]
    assert report.recommended_direction == "파일 크기에 따라 선택"
    assert client.responses.create.call_count == 1
    assert client.responses.parse.call_count == 3
    assert client.responses.parse.call_args_list[0].kwargs["text_format"] is ResearchPlan
    assert client.responses.create.call_args.kwargs["tool_choice"] == "required"
    assert client.responses.create.call_args.kwargs["max_tool_calls"] == MAX_TOOL_CALLS_PER_ROUND
    assert events.index(("plan_ready", 0, "file upload architecture official docs")) < events.index(
        ("search_start", 1, "file upload architecture official docs"))


def test_insufficient_runs_exactly_one_follow_up_and_merges_sources():
    first = search_response(urls=(SOURCE_A,), cited_url=None, evidence="First ref")
    second = search_response(urls=(SOURCE_A, SOURCE_B), cited_url=SOURCE_A,
                             evidence="Second ref")
    client = client_for([first, second], sufficient=False)

    report = generate_research_report("업로드 설계", client=client)

    assert report.search_queries == ["file upload architecture official docs",
                                     "presigned URL security official docs"]
    assert len(report.search_queries) == MAX_SEARCH_ROUNDS == 2
    assert client.responses.create.call_count == 2
    assert client.responses.parse.call_count == 3  # No assessment or search after round two.
    assert report.sources == [SOURCE_A, SOURCE_B]
    assert report.source_details[0].cited  # Second round upgrades the duplicate.
    assert report.citation_spans == [(len("First ref") + 2 + 9,
                                      len("First ref") + 2 + 12, "Cited docs", SOURCE_A)]
    assert "Second ref" in client.responses.parse.call_args.kwargs["input"][1]["content"]


def test_second_round_does_not_trigger_a_third_search():
    client = client_for([search_response(), search_response(urls=(SOURCE_B,),
                                                            cited_url=SOURCE_B)], sufficient=False)
    generate_research_report("업로드 설계", client=client)
    assert client.responses.create.call_count == MAX_SEARCH_ROUNDS
    assert all(call.kwargs["max_tool_calls"] == 1
               for call in client.responses.create.call_args_list)


def test_no_source_after_two_rounds_fails_before_report():
    no_source = search_response(urls=(), cited_url=None)
    client = client_for([no_source, no_source], sufficient=False)
    with pytest.raises(ResearchError, match="실제 출처"):
        generate_research_report("업로드 설계", client=client)
    assert client.responses.create.call_count == 2
    assert client.responses.parse.call_count == 2


def test_blank_topic_does_not_call_api():
    client = Obj(responses=Obj(create=Mock(), parse=Mock()))
    with pytest.raises(ValueError, match="must not be empty"):
        generate_research_report(" \n ", client=client)
    client.responses.create.assert_not_called()
    client.responses.parse.assert_not_called()


def test_missing_key_fails_before_api_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ResearchError, match="OPENAI_API_KEY"):
        generate_research_report("업로드 설계")


def test_api_error_is_wrapped_without_retry():
    client = Obj(responses=Obj(create=Mock(side_effect=OpenAIError("failure")),
                               parse=Mock(return_value=plan_response())))
    with pytest.raises(ResearchError, match="OpenAI API"):
        generate_research_report("업로드 설계", client=client)
    assert client.responses.create.call_count == 1
    assert client.responses.parse.call_count == 1


def test_model_backwards_compatible():
    report = ResearchReport("topic", ["r"], ["a"], ["c"], ["risk"], ["check"], ["mock"])
    assert report.recommended_direction == ""
    assert report.sources == ["mock"]
    assert report.research_plan is None


def test_evidence_citation_is_clickable_and_text_is_escaped():
    report = ResearchReport("topic", [], [], [], [], [], [],
                            search_evidence="<script> ref",
                            citation_spans=[(9, 12, "Official docs", SOURCE_A)])
    html = evidence_html(report)
    assert "&lt;script&gt;" in html
    assert f'<a href="{SOURCE_A}">Official docs</a>' in html
