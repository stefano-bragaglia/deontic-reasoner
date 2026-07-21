"""Propositional core types: atoms, worlds, weighted conditional rules, and hard constraints.

``Atom`` is the base propositional vocabulary; a ``World`` is the set of atoms true at
that world. ``Rule`` and ``HardConstraint`` are the two ways a norm set constrains which
worlds are preferred or possible, per the Preferential Dyadic Deontic Logic framework this
package implements.
"""

from dataclasses import dataclass

Atom = str
World = frozenset[str]


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
