from typing import Annotated, TypedDict

from .models import Clause, Finding, ParsedContract, RiskReport


def merge_findings(left: list[Finding], right: list[Finding]) -> list[Finding]:
    """Reducer: unchanged from Phase 1."""
    seen = {(f.clause_id, f.specialist, f.issue.casefold()) for f in left}
    merged = list(left)
    for f in right:
        key = (f.clause_id, f.specialist, f.issue.casefold())
        if key not in seen:
            seen.add(key)
            merged.append(f)
    return merged


class ReviewState(TypedDict):
    contract: ParsedContract                                   # CHANGED: input; replaces contract_text + clauses
    findings: Annotated[list[Finding], merge_findings]         # unchanged
    report: RiskReport                                         # unchanged


class ReviewTask(TypedDict):
    clause: Clause                                             # unchanged shape, but Clause is now richer