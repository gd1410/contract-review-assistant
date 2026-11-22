from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Specialist(StrEnum):
    LIABILITY = "liability"
    PRIVACY = "privacy"
    TERMINATION = "termination"


# ---------- NEW: ingestion enums ----------
class SourceFormat(StrEnum):
    DOCX = "docx"
    PDF = "pdf"
    TXT = "txt"


class SegmentationMethod(StrEnum):
    RULES = "rules"
    LLM = "llm"


# ---------- CHANGED: Clause is now richer ----------
class Clause(BaseModel):
    id: str                              # unique and STABLE, e.g. "c4.2" (approvals and dedupe depend on it)
    number: str | None = None            # as printed ("4.2"); None for unnumbered headings
    heading: str
    text: str                            # full text the reviewer sees
    breadcrumb: str = ""                 # "4. Data Handling > 4.2 Transfers": context for the LLM
    level: int = Field(default=1, ge=1)  # depth in the clause tree (1 = top level)
    parent_id: str | None = None
    page_start: int | None = None        # provenance: lets the UI jump to the page and,
    page_end: int | None = None          # later, anchor a redline in the Word file


# ---------- NEW: how trustworthy was the extraction? ----------
class IngestionReport(BaseModel):
    method: SegmentationMethod
    coverage: float = Field(ge=0, le=1)  # share of source text accounted for by clauses
    warnings: list[str] = Field(default_factory=list)
    needs_human_review: bool             # set by the pipeline using settings.min_coverage


# ---------- NEW: the single object that crosses the ingestion -> review boundary ----------
class ParsedContract(BaseModel):
    source_name: str
    source_format: SourceFormat
    clauses: list[Clause] = Field(min_length=1)   # fail-fast moved here: can't be bypassed
    ingestion: IngestionReport

    @model_validator(mode="after")
    def _clause_ids_are_unique(self) -> Self:
        ids = [c.id for c in self.clauses]
        if len(ids) != len(set(ids)):
            raise ValueError("Clause ids must be unique")
        return self


# ---------- unchanged: what the LLM produces ----------
class LLMFinding(BaseModel):
    """What the LLM is asked to produce. Nothing it could hallucinate about our own data."""

    issue: str = Field(description="One-sentence description of the risk")
    severity: Severity
    citation: str = Field(description="Exact quote from the clause (max 25 words) that shows the issue")
    suggested_redline: str = Field(description="Concrete replacement wording that fixes the issue")


class ReviewOutput(BaseModel):
    findings: list[LLMFinding] = Field(
        default_factory=list,
        description="Empty list if the clause raises no concern in your specialty",
    )


class Finding(LLMFinding):
    clause_id: str
    specialist: Specialist


# ---------- CHANGED: the report carries provenance ----------
class RiskReport(BaseModel):
    source_name: str                     # NEW
    overall_score: int = Field(ge=0, le=100)
    risk_level: Severity
    clause_count: int
    findings: list[Finding]
    ingestion: IngestionReport           # NEW: a reader can see how reliable the input extraction was