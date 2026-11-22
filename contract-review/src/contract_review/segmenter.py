import re

from .models import Clause

# Split before a newline followed by "<digits>. " (lookahead keeps the number in the clause).
_CLAUSE_SPLIT = re.compile(r"\n(?=\d+\.\s)")
_CLAUSE_HEAD = re.compile(r"^(?P<num>\d+)\.\s+(?P<heading>[^.\n]+)\.")


def segment_clauses(text: str) -> list[Clause]:
    clauses: list[Clause] = []
    for block in _CLAUSE_SPLIT.split(text.strip()):
        block = block.strip()
        match = _CLAUSE_HEAD.match(block)
        if match:  # preamble (title, parties) doesn't match and is skipped
            num = match["num"]
            heading = match["heading"].strip()
            clauses.append(
                Clause(
                    id=f"c{num}",
                    number=num,
                    heading=heading,
                    text=block,
                    breadcrumb=f"{num}. {heading}",
                )
            )
    return clauses