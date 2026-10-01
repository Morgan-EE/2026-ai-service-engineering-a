from dataclasses import dataclass, field


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
