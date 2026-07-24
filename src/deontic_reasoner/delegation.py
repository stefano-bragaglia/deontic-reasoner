"""Delegation obligations grounding: audit, dyadic revoke-on-violation, and liability.

Derives the delegator's oversight obligations straight from a single delegation fact, via
the same weighted-:class:`~deontic_reasoner.models.Rule` mechanism
:mod:`~deontic_reasoner.grounding` already uses for Hohfeldian correlatives — no separate
mechanism. The dyadic ("revoke only if violated") condition is represented by including the
violation atom in the revoke rule's body, the same conjunction technique used for every
other conditional obligation in this framework.
"""

from deontic_reasoner.models import Atom, Rule

OBLIGATION_WEIGHT = 1000.0
"""The default weight of a delegation obligation rule, high enough to dominate typical
domain-rule weights by convention; callers may override it via :func:`ground_delegation`'s
``weight`` parameter."""


def atom_for_delegation(delegator: str, delegatee: str, norm_id: str) -> Atom:
    """Build the deterministic atom asserting that a delegation fact holds.

    :param delegator: the agent who delegated the norm
    :param delegatee: the agent the norm was delegated to
    :param norm_id: the id of the delegated norm
    :return: an atom that is a deterministic function of the three arguments
    """
    return f"delegation:{delegator}:{delegatee}:{norm_id}"


def atom_for_violation(delegatee: str, norm_id: str) -> Atom:
    """Build the deterministic atom asserting that a delegatee violated a delegated norm.

    :param delegatee: the agent who violated the norm
    :param norm_id: the id of the violated norm
    :return: an atom that is a deterministic function of the two arguments
    """
    return f"violation:{delegatee}:{norm_id}"


def ground_delegation(
    delegator: str, delegatee: str, norm_id: str, weight: float = OBLIGATION_WEIGHT
) -> tuple[Rule, Rule, Rule]:
    """Ground a delegation fact to its audit, dyadic revoke, and liability rules.

    :param delegator: the agent who delegated the norm
    :param delegatee: the agent the norm was delegated to
    :param norm_id: the id of the delegated norm
    :param weight: the weight shared by all three derived rules
    :return: ``(audit_rule, revoke_rule, liable_rule)``, where ``audit_rule`` and
        ``liable_rule`` fire whenever the delegation atom alone holds, and ``revoke_rule``
        fires only when the delegation atom *and* the violation atom both hold
    """
    delegation_atom = atom_for_delegation(delegator, delegatee, norm_id)
    violation_atom = atom_for_violation(delegatee, norm_id)
    audit_atom = f"audit:{delegator}"
    revoke_atom = f"revoke:{delegator}"
    liability_atom = f"liability:{delegator}:{delegatee}"

    audit_rule = Rule(body=frozenset({delegation_atom}), head=frozenset({audit_atom}), weight=weight)
    revoke_rule = Rule(
        body=frozenset({delegation_atom, violation_atom}),
        head=frozenset({revoke_atom}),
        weight=weight,
    )
    liable_rule = Rule(
        body=frozenset({delegation_atom}), head=frozenset({liability_atom}), weight=weight
    )
    return audit_rule, revoke_rule, liable_rule
