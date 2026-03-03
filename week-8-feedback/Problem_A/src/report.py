from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Dict


@dataclass(frozen=True)
class DomainStat:
    domain: str
    hits: int


def top_k_domains(lines: Iterable[str], k: int) -> List[DomainStat]:
  
    if k <= 0:
        return []

    counts: Dict[str, int] = {}
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        counts[s] = counts.get(s, 0) + 1

    items = list(counts.items())
    items.sort(key=lambda t: t[1], reverse=True)

    return [DomainStat(domain=d, hits=c) for d, c in items[:k]]