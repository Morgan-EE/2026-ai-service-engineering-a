from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchReport:
    topic: str
    requirements_summary: list[str]
    approaches: list[str]
    comparison: list[str]
    risks: list[str]
    checklist: list[str]
    sources: list[str]
