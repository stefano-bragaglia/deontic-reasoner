"""Rule violation and hard-constraint exclusion — the first behavioral layer over the core data model.

Everything else in the preference-ordering/best-worlds machinery builds on
:func:`violates` and :func:`excludes`.
"""

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
