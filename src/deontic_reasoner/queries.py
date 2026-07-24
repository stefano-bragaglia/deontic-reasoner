"""Obligation and permissibility queries — Hansson's dyadic ``O(q|p)`` and its permission dual.

Built directly on :func:`~deontic_reasoner.preference.best_worlds`: an obligation query
asks whether ``b`` holds at *every* best world, a permissibility query whether it holds
at *some* best world.
"""

from collections.abc import Iterable

from deontic_reasoner.models import Atom, HardConstraint, Rule, World
from deontic_reasoner.preference import PreferenceCriterion, best_worlds


def is_obligatory(
    b: frozenset[Atom],
    given: frozenset[Atom],
    rules: Iterable[Rule],
    hard_constraints: Iterable[HardConstraint] = (),
    criterion: PreferenceCriterion = PreferenceCriterion.WEIGHTED_COUNT,
) -> bool:
    """Check whether ``b`` is obligatory given ``given``.

    :param b: the conjunction of atoms to check
    :param given: the antecedent every best world must satisfy
    :param rules: the rules candidate worlds are evaluated against
    :param hard_constraints: constraints that exclude a candidate world entirely
    :param criterion: which :class:`~deontic_reasoner.preference.PreferenceCriterion` to
        rank worlds by
    :return: ``True`` iff ``b`` holds at every world in
        :func:`~deontic_reasoner.preference.best_worlds`'s result for ``given`` (vacuously
        ``True`` if that result is empty)
    """
    worlds: set[World] = best_worlds(given, rules, hard_constraints, criterion)
    return all(b <= world for world in worlds)


def is_permitted(
    b: frozenset[Atom],
    given: frozenset[Atom],
    rules: Iterable[Rule],
    hard_constraints: Iterable[HardConstraint] = (),
    criterion: PreferenceCriterion = PreferenceCriterion.WEIGHTED_COUNT,
) -> bool:
    """Check whether ``b`` is permitted given ``given``.

    :param b: the conjunction of atoms to check
    :param given: the antecedent every best world must satisfy
    :param rules: the rules candidate worlds are evaluated against
    :param hard_constraints: constraints that exclude a candidate world entirely
    :param criterion: which :class:`~deontic_reasoner.preference.PreferenceCriterion` to
        rank worlds by
    :return: ``True`` iff ``b`` holds at some world in
        :func:`~deontic_reasoner.preference.best_worlds`'s result for ``given`` (vacuously
        ``False`` if that result is empty)
    """
    worlds: set[World] = best_worlds(given, rules, hard_constraints, criterion)
    return any(b <= world for world in worlds)
