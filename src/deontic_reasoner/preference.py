"""Rule violation, hard-constraint exclusion, and preference ordering over worlds.

Everything else in the preference-ordering/best-worlds machinery builds on
:func:`violates` and :func:`excludes`. :func:`preferred` is what directly replaces the
superseded SAT-based conflict detection and combining algorithms: which world "wins" falls
out of comparing violated-rule sets, no separate machinery needed.
"""

from collections.abc import Iterable
from enum import Enum, auto

from deontic_reasoner.models import HardConstraint, Rule, World


def violates(rule: Rule, world: World) -> bool:
    """Check whether ``world`` makes ``rule``'s body true but its head false.

    :param rule: the rule to check
    :param world: the world to check it against
    :return: ``True`` iff ``rule.body`` holds in ``world`` and ``rule.head`` does not
    """
    return rule.body <= world and not rule.head <= world


def excludes(constraint: HardConstraint, world: World) -> bool:
    """Check whether ``constraint`` rules ``world`` out entirely.

    :param constraint: the hard constraint to check
    :param world: the world to check it against
    :return: ``True`` iff ``constraint.forbidden`` is non-empty and every atom in it is
        present in ``world``
    """
    return bool(constraint.forbidden) and constraint.forbidden <= world


class PreferenceCriterion(Enum):
    """Which criterion :func:`preferred` compares two worlds' violated-rule sets under."""

    SUBSET = auto()
    COUNT = auto()
    WEIGHTED_COUNT = auto()


def violated_rules(world: World, rules: Iterable[Rule]) -> frozenset[Rule]:
    """Collect exactly the rules in ``rules`` that ``world`` violates.

    :param world: the world to check
    :param rules: the candidate rules to check it against
    :return: the subset of ``rules`` for which :func:`violates` holds against ``world``
    """
    return frozenset(rule for rule in rules if violates(rule, world))


def _weight_sort_key(rule: Rule) -> tuple[list[str], list[str], float]:
    """Build a stable sort key for a rule, independent of ``frozenset``/``hash()`` order.

    :param rule: the rule to build a key for
    :return: a key derived only from string comparison of ``body``/``head``, never from
        hash values, so summation order stays identical across separate process runs
        despite Python's per-process string-hash randomization
    """
    return sorted(rule.body), sorted(rule.head), rule.weight


def _total_weight(rules: frozenset[Rule]) -> float:
    """Sum a set of rules' weights in a deterministic, hash-independent order.

    :param rules: the rules to sum
    :return: the sum of every rule's ``weight``, in a stable order
    """
    return sum(rule.weight for rule in sorted(rules, key=_weight_sort_key))


def preferred(
    world_a: World,
    world_b: World,
    rules: Iterable[Rule],
    criterion: PreferenceCriterion = PreferenceCriterion.WEIGHTED_COUNT,
) -> bool:
    """Check whether ``world_a`` is at least as preferred as ``world_b``.

    :param world_a: the candidate world
    :param world_b: the world to compare it against
    :param rules: the rules both worlds are evaluated against
    :param criterion: which comparison criterion to use over each world's violated-rule set
    :return: ``True`` iff ``world_a`` is at least as preferred as ``world_b`` under
        ``criterion``
    """
    rules = list(rules)
    violated_a = violated_rules(world_a, rules)
    violated_b = violated_rules(world_b, rules)
    if criterion is PreferenceCriterion.SUBSET:
        return violated_a <= violated_b
    if criterion is PreferenceCriterion.COUNT:
        return len(violated_a) <= len(violated_b)
    return _total_weight(violated_a) <= _total_weight(violated_b)
