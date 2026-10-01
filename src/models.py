from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    goal: str = Field(min_length=1)
    key_questions: list[str] = Field(min_length=1)
    perspectives: list[str] = Field(min_length=1)
    search_query: str = Field(min_length=1)


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    cited: bool = False


@dataclass(frozen=True)
class ResearchReport:
    topic: str
    requirements_summary: list[str]
    approaches: list[str]
    comparison: list[str]
    risks: list[str]
    checklist: list[str]
    sources: list[str]
    recommended_direction: str = ""
    source_details: list[Source] = field(default_factory=list)
    search_evidence: str = ""
    citation_spans: list[tuple[int, int, str, str]] = field(default_factory=list)
    research_plan: ResearchPlan | None = None
    search_queries: list[str] = field(default_factory=list)
