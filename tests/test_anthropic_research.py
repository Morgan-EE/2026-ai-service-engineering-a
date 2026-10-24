import json
import socket
from types import SimpleNamespace as Obj
from unittest.mock import Mock

import pytest
import httpx2
from anthropic import Anthropic
from pydantic import ValidationError

from src.models import ResearchPlan
from src.web_research import (
    ANTHROPIC_ASSESSMENT_TOKENS,
    ANTHROPIC_PLAN_TOKENS,
    ANTHROPIC_REPORT_TOKENS,
    ANTHROPIC_SEARCH_TOKENS,
    ReportSections,
    ResearchError,
    SufficiencyAssessment,
    _anthropic_structured,
    generate_research_report,
)


SOURCE = "https://docs.example.com/remove-background"


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    # Windows asyncio uses a loopback socket pair even for in-process UI tests.
    def local_only(original):
        def connect(sock, address, *args, **kwargs):
            if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
                return original(sock, address, *args, **kwargs)
            raise AssertionError("External network access is forbidden in Claude regression tests")
        return connect

    monkeypatch.setattr(socket.socket, "connect", local_only(socket.socket.connect))
    monkeypatch.setattr(socket.socket, "connect_ex", local_only(socket.socket.connect_ex))


def structured(value):
    return Obj(stop_reason="end_turn", content=[Obj(type="text", text=json.dumps(value))])


def professional_sections():
    return {
        "executive_summary": [
            "고품질 누끼는 분할 마스크와 알파 매팅 품질에 좌우된다.",
            "대량 처리에는 비동기 작업 큐와 품질 게이트가 필요하다.",
        ],
        "technical_scope": ["RGB 입력에서 투명 PNG 출력까지의 파이프라인", "머리카락·반투명 경계 처리"],
        "decision_criteria": ["경계 IoU", "알파 경계 품질", "p95 지연 시간"],
        "requirements_summary": ["입력 정규화", "알파 채널 출력"],
        "approaches": ["세맨틱 세그멘테이션", "알파 매팅 보정"],
        "approach_details": [
            {"name": "세맨틱 세그멘테이션", "architecture": "인코더-디코더가 전경 확률 마스크를 생성한다.", "best_fit": "명확한 전경", "strengths": ["낮은 지연"], "tradeoffs": ["미세 경계 손실"], "implementation_steps": ["입력 이미지 정규화", "모델 추론 후 알파 PNG 합성"]},
            {"name": "알파 매팅 보정", "architecture": "트라이맵 또는 마스크 경계를 알파 값으로 재추정한다.", "best_fit": "머리카락과 반투명 물체", "strengths": ["경계 품질"], "tradeoffs": ["추가 추론 비용"], "implementation_steps": ["불확실한 경계 영역 추출", "매팅 모델로 알파 값 재추정"]},
        ],
        "comparison": ["매팅은 품질이 높지만 비용이 크다.", "세그멘테이션은 실시간 경로에 유리하다."],
        "recommended_direction": "기본 세그멘테이션 뒤 불확실 경계만 매팅으로 보정한다.",
        "implementation_plan": ["입력 정규화", "비동기 추론 큐", "알파 PNG 저장"],
        "validation_plan": ["경계 라벨 세트 평가", "p95 측정", "실패 이미지 회귀 테스트"],
        "risks": ["역광 경계 오류", "개인 이미지 보관"],
        "checklist": ["EXIF 제거", "입력 크기 제한", "알파 품질 관측"],
        "evidence_limitations": ["실제 모델별 점수는 대상 데이터셋에서 재측정해야 한다."],
        "commercial_examples": [{
            "product": "Example Cutout (테스트용 가상 제품)", "observed_features": "배경 제거 API와 마스크 보정",
            "disclosed_implementation": "내부 구현 비공개/미확인",
            "implementation_takeaway": "배경 제거 엔드포인트와 마스크 편집 UI를 구현한다.",
            "evidence_status": "not_disclosed", "source_urls": [SOURCE],
        }],
    }


def search_response():
    return Obj(
        stop_reason="end_turn",
        content=[
            Obj(type="server_tool_use", name="web_search"),
            Obj(type="web_search_tool_result", content=[Obj(type="web_search_result", title="Official guide", url=SOURCE)]),
            Obj(type="text", text="경계 품질은 알파 매팅 단계에서 개선된다.", citations=[Obj(title="Official guide", url=SOURCE)]),
        ],
    )


def test_claude_path_uses_web_search_and_produces_technical_sections_without_network(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    plan = {"goal": "배경 제거 파이프라인 선택", "key_questions": ["경계 품질은?"], "perspectives": ["품질", "지연"], "search_query": "image matting technical documentation", "commercial_search_query": "commercial background removal official API engineering docs"}
    assessment = {"sufficient": True, "missing_points": [], "follow_up_query": None}
    client = Obj(messages=Obj(create=Mock(side_effect=[structured(plan), search_response(), structured(assessment), search_response(), structured(professional_sections())])))

    report = generate_research_report("사진에서 누끼 따는 법을 조사해줘", client=client, provider="anthropic")

    assert report.provider == "Claude (Anthropic)"
    assert report.approach_details[1].name == "알파 매팅 보정"
    assert report.validation_plan
    assert report.source_details[0].cited
    search_call = client.messages.create.call_args_list[1].kwargs
    assert search_call["tools"][0]["type"] == "web_search_20250305"
    assert search_call["tools"][0]["max_uses"] == 1
    assert "format" not in search_call.get("output_config", {})
    calls = [call.kwargs for call in client.messages.create.call_args_list]
    assert [call["max_tokens"] for call in calls] == [
        ANTHROPIC_PLAN_TOKENS, ANTHROPIC_SEARCH_TOKENS,
        ANTHROPIC_ASSESSMENT_TOKENS, ANTHROPIC_SEARCH_TOKENS, ANTHROPIC_REPORT_TOKENS,
    ]
    assert all(call["thinking"] == {"type": "between_tools"} for call in calls)
    assert all(call["output_config"]["effort"] == "medium" for call in calls)
    assert "commercial background removal" in calls[3]["messages"][0]["content"]
    assert report.commercial_examples[0].source_urls == [SOURCE]
    assert report.commercial_examples[0].evidence_status == "not_disclosed"


def test_claude_missing_key_fails_before_client_creation(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ResearchError, match="ANTHROPIC_API_KEY"):
        generate_research_report("누끼 파이프라인", provider="anthropic")


def assert_claude_schema_supported(schema):
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            assert schema.get("additionalProperties") is False
        assert "minLength" not in schema
        assert "maxLength" not in schema
        if "minItems" in schema:
            assert schema["minItems"] in (0, 1)
        for value in schema.values():
            assert_claude_schema_supported(value)
    elif isinstance(schema, list):
        for value in schema:
            assert_claude_schema_supported(value)


PLAN = {
    "goal": "배경 제거 구현 방법 선택",
    "key_questions": ["경계 품질 검증 방법은?"],
    "perspectives": ["품질", "비용"],
    "search_query": "image matting official documentation",
}


@pytest.mark.parametrize("model_type,payload", [
    (ResearchPlan, PLAN),
    (SufficiencyAssessment, {"sufficient": True, "missing_points": [], "follow_up_query": None}),
    (ReportSections, professional_sections()),
])
def test_real_sdk_sends_compatible_schema_to_in_memory_transport(model_type, payload):
    requests = []

    def handler(request):
        requests.append(request)
        body = json.loads(request.content)
        schema = body["output_config"]["format"]["schema"]
        assert_claude_schema_supported(schema)
        assert body["thinking"] == {"type": "between_tools"}
        assert body["output_config"]["effort"] == "medium"
        assert "tools" not in body  # Citations and JSON output remain separate.
        return httpx2.Response(200, json={
            "id": "msg_offline", "type": "message", "role": "assistant",
            "model": body["model"], "stop_reason": "end_turn", "stop_sequence": None,
            "content": [{"type": "text", "text": json.dumps(payload)}],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        })

    with Anthropic(api_key="offline-placeholder", max_retries=0,
                   http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
        result = _anthropic_structured(client, "claude-sonnet-5-5", model_type, "system", "topic", 2048)

    assert result == model_type.model_validate(payload)
    assert len(requests) == 1


@pytest.mark.parametrize("reason,content,expected", [
    ("max_tokens", [{"type": "thinking", "thinking": "PRIVATE_THINKING"}], "max_tokens"),
    ("max_tokens", [{"type": "text", "text": json.dumps(PLAN)}], "max_tokens"),
    ("refusal", [{"type": "text", "text": "PRIVATE_REFUSAL"}], "refusal"),
    ("pause_turn", [], "pause_turn"),
    ("end_turn", [{"type": "thinking", "thinking": "PRIVATE_THINKING"}], "empty_text"),
])
def test_incomplete_plan_reports_cause_and_never_searches_or_retries(reason, content, expected):
    client = Obj(messages=Obj(create=Mock(return_value=Obj(stop_reason=reason, content=content))))
    with pytest.raises(ResearchError) as caught:
        generate_research_report("이미지 누끼따는 기능을 구현하고싶어 조사해줘", client=client, provider="anthropic")
    assert "조사 계획" in str(caught.value)
    assert expected in str(caught.value)
    assert "PRIVATE" not in str(caught.value)
    client.messages.create.assert_called_once()


def test_truncated_report_is_not_returned_even_when_partial_json_is_valid():
    responses = [
        structured(PLAN), search_response(),
        structured({"sufficient": True, "missing_points": [], "follow_up_query": None}),
        search_response(),
        Obj(stop_reason="max_tokens", content=[Obj(type="text", text=json.dumps(professional_sections()))]),
    ]
    client = Obj(messages=Obj(create=Mock(side_effect=responses)))
    with pytest.raises(ResearchError, match="보고서 작성.*max_tokens"):
        generate_research_report("누끼 기능 구현", client=client, provider="anthropic")
    assert client.messages.create.call_count == 5


def test_other_models_do_not_receive_sonnet_55_thinking_mode():
    client = Obj(messages=Obj(create=Mock(return_value=structured(PLAN))))
    _anthropic_structured(client, "claude-sonnet-4-6", ResearchPlan, "system", "topic", 2048)
    request = client.messages.create.call_args.kwargs
    assert "thinking" not in request
    assert "effort" not in request["output_config"]


def test_local_quality_constraints_remain_enforced():
    invalid = dict(PLAN, goal="")
    client = Obj(messages=Obj(create=Mock(return_value=structured(invalid))))
    with pytest.raises(ValidationError):
        _anthropic_structured(client, "offline-model", ResearchPlan, "system", "topic", 750)


def test_bad_request_shows_stage_and_schema_hint_without_echoing_server_content():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx2.Response(400, json={
            "type": "error", "error": {"type": "invalid_request_error",
                "message": "output_config.format.schema: unsupported minLength; PRIVATE_PAYLOAD"},
        })

    with Anthropic(api_key="offline-placeholder", max_retries=0,
                   http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
        with pytest.raises(ResearchError) as caught:
            generate_research_report("누끼 기능 구현", client=client, provider="anthropic")

    message = str(caught.value)
    assert "HTTP 400" in message
    assert "조사 계획" in message
    assert "스키마" in message
    assert "PRIVATE_PAYLOAD" not in message
    assert "offline-placeholder" not in message
    assert len(requests) == 1


def commercial_client(sections):
    return Obj(messages=Obj(create=Mock(side_effect=[
        structured(PLAN), search_response(),
        structured({"sufficient": True, "missing_points": [], "follow_up_query": None}),
        search_response(), structured(sections),
    ])))


@pytest.mark.parametrize("source_urls", [[], ["https://invented.example/not-returned-by-search"]])
def test_commercial_claim_without_recorded_source_is_rejected(source_urls):
    sections = professional_sections()
    sections["commercial_examples"][0]["source_urls"] = source_urls
    client = commercial_client(sections)
    with pytest.raises(ResearchError, match="상용 사례"):
        generate_research_report("누끼 기능 구현", client=client, provider="anthropic")
    assert client.messages.create.call_count == 5


def test_no_verified_commercial_case_is_explicit_in_markdown():
    from src.markdown_export import report_to_markdown

    sections = professional_sections()
    sections["commercial_examples"] = []
    report = generate_research_report("누끼 기능 구현", client=commercial_client(sections), provider="anthropic")
    assert "공식 자료로 확인한 상용 사례가 없습니다" in report_to_markdown(report)


def test_streamlit_shows_results_and_commercial_cases_before_detailed_report(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    report = generate_research_report("누끼 기능 구현", client=commercial_client(professional_sections()), provider="anthropic")
    monkeypatch.setattr("src.web_research.generate_research_report", lambda *args, **kwargs: report)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.text_area[0].input("이미지 누끼 기능 구현")
    app.button[0].click().run()

    assert not app.exception
    headings = [item.value for item in app.subheader]
    assert headings.index("조사 결과 · 구현 방식 요약") < headings.index("Executive Summary")
    assert headings.index("상용 프로그램 사례와 적용 설계") < headings.index("Executive Summary")
    content = "\n".join(item.value for item in app.markdown)
    assert "구현 방식에는 크게 세맨틱 세그멘테이션, 알파 매팅 보정 등이 있습니다." in content
    assert "1. 입력 이미지 정규화" in content
    assert "Example Cutout (테스트용 가상 제품)" in content
    assert "내부 구현 비공개/미확인" in content
