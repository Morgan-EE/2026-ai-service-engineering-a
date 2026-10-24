from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    goal: str = Field(min_length=1)
    key_questions: list[str] = Field(min_length=1)
    perspectives: list[str] = Field(min_length=1)
    search_query: str = Field(min_length=1)
    commercial_search_query: str = ""


class ApproachDetail(BaseModel):
    """A technically actionable option considered in a research report."""

    name: str = Field(min_length=1)
    architecture: str = Field(min_length=1)
    best_fit: str = Field(min_length=1)
    strengths: list[str] = Field(min_length=1)
    tradeoffs: list[str] = Field(min_length=1)
    implementation_steps: list[str] = Field(min_length=2)


class CommercialExample(BaseModel):
    product: str = Field(min_length=1)
    observed_features: str = Field(min_length=1)
    disclosed_implementation: str = Field(min_length=1)
    implementation_takeaway: str = Field(min_length=1)
    evidence_status: Literal["documented", "not_disclosed", "unverified"]
    source_urls: list[str]


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
    provider: str = ""
    executive_summary: list[str] = field(default_factory=list)
    technical_scope: list[str] = field(default_factory=list)
    decision_criteria: list[str] = field(default_factory=list)
    approach_details: list[ApproachDetail] = field(default_factory=list)
    implementation_plan: list[str] = field(default_factory=list)
    validation_plan: list[str] = field(default_factory=list)
    evidence_limitations: list[str] = field(default_factory=list)
    commercial_examples: list[CommercialExample] = field(default_factory=list)
