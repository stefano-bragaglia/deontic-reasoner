"""Propositional core types: atoms, worlds, weighted conditional rules, and hard constraints.

``Atom`` is the base propositional vocabulary; a ``World`` is the set of atoms true at
that world. ``Rule`` and ``HardConstraint`` are the two ways a norm set constrains which
worlds are preferred or possible, per the Preferential Dyadic Deontic Logic framework this
package implements.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

Atom = str
World = frozenset[str]


class Relation(StrEnum):
    """The four Hohfeldian incidents a :class:`Norm` can ground."""

    PRIVILEGE = "privilege"
    RIGHT = "right"
    POWER = "power"
    IMMUNITY = "immunity"


@dataclass(frozen=True, slots=True)
class Rule:
    """A defeasible conditional rule: ``body`` (if satisfied) ought to imply ``head``.

    :param head: the conjunction of atoms that ought to hold when ``body`` is satisfied
    :param weight: the cost, under weighted-count preference, of a world violating this rule
    :param body: the conjunction of atoms that must hold for this rule to apply; an empty
        body is vacuously satisfied by every world, making the rule unconditional
    """

    head: frozenset[Atom]
    weight: float
    body: frozenset[Atom] = frozenset()


@dataclass(frozen=True, slots=True)
class HardConstraint:
    """A combination of atoms that can never hold together in any considered world.

    :param forbidden: the conjunction of atoms that may never all be true simultaneously;
        an empty set never excludes any world
    """

    forbidden: frozenset[Atom]


@dataclass(frozen=True, slots=True)
class Norm:
    """A single Hohfeldian incident, grounding a directed or undirected normative relation.

    :param id: a unique identifier for this norm
    :param relation: which of the four Hohfeldian incidents this norm asserts
    :param subject: the agent this norm is about
    :param action: the action the norm concerns
    :param resource: the resource the action targets
    :param counterparty: the correlative bearer of a directed relation (``right``/``power``/
        ``immunity``); ``None`` if this norm has no counterparty
    :param valid_from: the earliest time this norm applies; ``None`` means unbounded
    :param valid_until: the latest time this norm applies; ``None`` means unbounded
    :param condition: an additional named applicability guard beyond the temporal bounds;
        ``None`` means no extra guard
    """

    id: str
    relation: Relation
    subject: str
    action: str
    resource: str
    counterparty: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    condition: Atom | None = None
