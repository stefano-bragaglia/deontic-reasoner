"""Hohfeldian norm grounding: a norm's own atom, plus its correlative rule.

Correlativity (a ``right`` implies the counterparty's ``duty``, a ``power`` implies the
counterparty's ``liability``, an ``immunity`` implies the counterparty's ``disability``) is
represented as an ordinary weighted :class:`~deontic_reasoner.models.Rule`, not a
:class:`~deontic_reasoner.models.HardConstraint` — a hard constraint would make it
impossible to ever demonstrate the correlative duty being violated.
"""

from deontic_reasoner.models import Atom, Norm, Relation, Rule

CORRELATIVE_WEIGHT = 1000.0
"""The default weight of a correlative rule, high enough to dominate typical domain-rule
weights by convention; callers may override it via :func:`ground_norm`'s ``weight``
parameter."""

_CORRELATIVE_WORD = {
    Relation.RIGHT: "duty",
    Relation.POWER: "liability",
    Relation.IMMUNITY: "disability",
}


def atom_for_norm(norm: Norm) -> Atom:
    """Build the deterministic atom asserting that ``norm`` holds.

    :param norm: the norm to name an atom for
    :return: an atom that is a deterministic function of ``norm.id`` alone
    """
    return f"norm:{norm.id}"


def ground_norm(norm: Norm, weight: float = CORRELATIVE_WEIGHT) -> tuple[Atom, Rule | None]:
    """Ground a norm to its own atom, plus its correlative rule if it has one.

    :param norm: the norm to ground
    :param weight: the weight of the correlative rule, if one is produced
    :return: ``(atom_for_norm(norm), rule)``, where ``rule`` derives the counterparty's
        correlative duty/liability/disability atom from ``norm``'s own atom; ``rule`` is
        ``None`` for a ``privilege`` norm, or when ``norm.counterparty`` is ``None``
    """
    atom = atom_for_norm(norm)
    word = _CORRELATIVE_WORD.get(norm.relation)
    if word is None or norm.counterparty is None:
        return atom, None
    head_atom = f"{word}:{norm.counterparty}:{norm.action}:{norm.resource}"
    rule = Rule(body=frozenset({atom}), head=frozenset({head_atom}), weight=weight)
    return atom, rule
