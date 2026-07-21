from dataclasses import dataclass

Atom = str
World = frozenset[str]


@dataclass(frozen=True, slots=True)
class Rule:
    head: frozenset[Atom]
    weight: float
    body: frozenset[Atom] = frozenset()


@dataclass(frozen=True, slots=True)
class HardConstraint:
    forbidden: frozenset[Atom]
