"""One bounded web search followed by one structured report conversion."""

import os
from urllib.parse import urlparse

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

from src.models import ResearchReport, Source


DEFAULT_MODEL = "gpt-4.1-mini"


class ResearchError(Exception):
    """A research request could not produce a sourced report."""


class ReportSections(BaseModel):
    requirements_summary: list[str] = Field(min_length=1)
    approaches: list[str] = Field(min_length=1)
    comparison: list[str] = Field(min_length=1)
    recommended_direction: str = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
    checklist: list[str] = Field(min_length=1)


def _value(item, key, default=None):
    return item.get(key, default) if isinstance(item, dict) else getattr(item, key, default)


def _valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _search_metadata(response):
    sources: dict[str, Source] = {}
    spans: list[tuple[int, int, str, str]] = []
    searched = False
    for item in _value(response, "output", []):
        if _value(item, "type") == "web_search_call" and _value(item, "status") == "completed":
            searched = True
            for raw in _value(_value(item, "action"), "sources", []) or []:
                url = _value(raw, "url", "")
                if _valid_url(url):
                    sources.setdefault(url, Source(_value(raw, "title") or url, url))
        if _value(item, "type") == "message":
            for content in _value(item, "content", []):
                for annotation in _value(content, "annotations", []) or []:
                    if _value(annotation, "type") != "url_citation":
                        continue
                    url = _value(annotation, "url", "")
                    if not _valid_url(url):
                        continue
                    title = _value(annotation, "title") or url
                    sources[url] = Source(title, url, cited=True)
                    start = _value(annotation, "start_index")
                    end = _value(annotation, "end_index")
                    if isinstance(start, int) and isinstance(end, int):
                        spans.append((start, end, title, url))
    return searched, list(sources.values()), spans


def generate_research_report(topic: str, client=None) -> ResearchReport:
    topic = topic.strip()
    if not topic:
        raise ValueError("Research topic must not be empty")
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ResearchError("OPENAI_API_KEY 환경변수를 설정해 주세요.")
        client = OpenAI(api_key=api_key, timeout=45.0, max_retries=0)

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    try:
        search = client.responses.create(
            model=model,
            tools=[{"type": "web_search", "search_context_size": "medium"}],
            tool_choice="required",
            max_tool_calls=2,
            max_output_tokens=1800,
            include=["web_search_call.action.sources"],
            input=(
                "다음 개발 기술 조사 주제를 웹에서 조사하세요. 공식 문서와 신뢰할 수 있는 "
                "기술 자료를 우선하고, 후보 방식의 선택 기준·위험을 근거와 함께 요약하세요. "
                "사용한 자료는 인라인 인용으로 표시하세요.\n\n조사 주제: " + topic
            ),
        )
        searched, sources, spans = _search_metadata(search)
        evidence = _value(search, "output_text", "") or ""
        if _value(search, "status") != "completed" or not searched or not evidence or not sources:
            raise ResearchError("검색 결과 또는 실제 출처를 확인할 수 없어 보고서를 생성하지 않았습니다.")

        structured = client.responses.parse(
            model=model,
            text_format=ReportSections,
            max_output_tokens=1800,
            input=[
                {"role": "system", "content": (
                    "You create a concise Korean engineering research report from supplied web evidence. "
                    "Use only the evidence provided. Do not invent citations, URLs, or facts. "
                    "If evidence is insufficient, identify that limitation in risks."
                )},
                {"role": "user", "content": (
                    f"조사 주제: {topic}\n\n검색 조사 내용:\n{evidence}\n\n"
                    "출처 URL은 프로그램이 API 메타데이터에서 별도로 표시합니다. "
                    "각 섹션을 근거에 맞게 한국어로 작성하세요."
                )},
            ],
        )
        sections = _value(structured, "output_parsed")
        if _value(structured, "status") != "completed" or sections is None:
            raise ResearchError("구조화된 보고서를 생성하지 못했습니다.")
        return ResearchReport(
            topic=topic,
            requirements_summary=sections.requirements_summary,
            approaches=sections.approaches,
            comparison=sections.comparison,
            risks=sections.risks,
            checklist=sections.checklist,
            sources=[source.url for source in sources],
            recommended_direction=sections.recommended_direction,
            source_details=sources,
            search_evidence=evidence,
            citation_spans=spans,
        )
    except OpenAIError as exc:
        raise ResearchError(f"OpenAI API 요청에 실패했습니다: {exc.__class__.__name__}") from exc
    except ValidationError as exc:
        raise ResearchError("보고서 형식 검증에 실패했습니다.") from exc
