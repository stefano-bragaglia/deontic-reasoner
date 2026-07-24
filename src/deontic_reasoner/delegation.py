"""Delegation obligations grounding: audit, dyadic revoke-on-violation, and liability.

Derives the delegator's oversight obligations straight from a single delegation fact, via
the same weighted-:class:`~deontic_reasoner.models.Rule` mechanism
:mod:`~deontic_reasoner.grounding` already uses for Hohfeldian correlatives — no separate
mechanism. The dyadic ("revoke only if violated") condition is represented by including the
violation atom in the revoke rule's body, the same conjunction technique used for every
other conditional obligation in this framework.
"""

from datetime import datetime

from deontic_reasoner.models import Atom, Norm, Relation, Rule

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


def exercise_power(
    power_norm: Norm,
    subject: str,
    relation: Relation,
    action: str,
    resource: str,
    counterparty: str | None = None,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
    condition: Atom | None = None,
) -> Norm:
    """Construct the new norm a Hohfeldian power's exercise brings into existence.

    :param power_norm: the norm granting the power being exercised
    :param subject: the agent the new norm is about
    :param relation: which Hohfeldian incident the new norm asserts
    :param action: the action the new norm concerns
    :param resource: the resource the action targets
    :param counterparty: the correlative bearer of the new norm, if directed
    :param valid_from: the earliest time the new norm applies
    :param valid_until: the latest time the new norm applies
    :param condition: an additional named applicability guard for the new norm
    :return: a new :class:`Norm` whose ``id`` is a deterministic function of
        ``power_norm.id``, ``subject``, ``relation``, ``action``, ``resource``, and
        ``counterparty`` — calling this twice with identical arguments returns two equal
        norms, so feeding the result into a forward-chaining loop twice is a no-op
    """
    new_id = f"exercise:{power_norm.id}:{subject}:{relation}:{action}:{resource}:{counterparty}"
    return Norm(
        id=new_id,
        relation=relation,
        subject=subject,
        action=action,
        resource=resource,
        counterparty=counterparty,
        valid_from=valid_from,
        valid_until=valid_until,
        condition=condition,
    )


def _narrow_lower_bound(parent_bound: datetime | None, candidate_bound: datetime | None) -> datetime | None:
    if parent_bound is None:
        return candidate_bound
    if candidate_bound is None:
        return parent_bound
    return max(parent_bound, candidate_bound)


def _narrow_upper_bound(parent_bound: datetime | None, candidate_bound: datetime | None) -> datetime | None:
    if parent_bound is None:
        return candidate_bound
    if candidate_bound is None:
        return parent_bound
    return min(parent_bound, candidate_bound)


def delegate_with_narrowing(
    parent: Norm,
    subject: str,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
    counterparty: str | None = None,
    condition: Atom | None = None,
) -> Norm:
    """Derive a delegatee's norm from ``parent``, narrowing the temporal window to their intersection.

    :param parent: the delegator's own norm being delegated
    :param subject: the delegatee the new norm is granted to
    :param valid_from: the candidate lower temporal bound; may be wider than ``parent``'s own
    :param valid_until: the candidate upper temporal bound; may be wider than ``parent``'s own
    :param counterparty: the correlative bearer of the new norm, if directed
    :param condition: an additional named applicability guard for the new norm
    :return: a new :class:`Norm` with ``parent``'s ``relation``/``action``/``resource``
        unchanged, and ``valid_from``/``valid_until`` narrowed to the intersection of
        ``parent``'s window and the candidate window — never wider than ``parent``'s own;
        its ``id`` is a deterministic function of ``(parent.id, subject, valid_from,
        valid_until, counterparty, condition)``
    """
    new_id = f"delegate:{parent.id}:{subject}:{valid_from}:{valid_until}:{counterparty}:{condition}"
    return Norm(
        id=new_id,
        relation=parent.relation,
        subject=subject,
        action=parent.action,
        resource=parent.resource,
        counterparty=counterparty,
        valid_from=_narrow_lower_bound(parent.valid_from, valid_from),
        valid_until=_narrow_upper_bound(parent.valid_until, valid_until),
        condition=condition,
    )
