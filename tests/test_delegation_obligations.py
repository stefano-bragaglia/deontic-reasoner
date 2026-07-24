from deontic_reasoner.delegation import (
    OBLIGATION_WEIGHT,
    atom_for_delegation,
    atom_for_violation,
    ground_delegation,
)
from deontic_reasoner.queries import is_obligatory

_DELEGATOR = "Orchestrator"
_DELEGATEE = "DataAgent"
_NORM_ID = "n1"


def test_atom_for_delegation_is_deterministic():
    args = (_DELEGATOR, _DELEGATEE, _NORM_ID)
    assert atom_for_delegation(*args) == atom_for_delegation(*args)


def test_ground_delegation_returns_three_rules_with_default_weight():
    audit_rule, revoke_rule, liable_rule = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    for rule in (audit_rule, revoke_rule, liable_rule):
        assert rule.weight == OBLIGATION_WEIGHT


def test_ground_delegation_is_deterministic_across_repeated_calls():
    first = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    second = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    assert first == second


def test_audit_and_liable_rules_body_is_exactly_the_delegation_atom():
    delegation_atom = atom_for_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    audit_rule, _, liable_rule = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    assert audit_rule.body == frozenset({delegation_atom})
    assert liable_rule.body == frozenset({delegation_atom})


def test_revoke_rule_body_is_delegation_atom_and_violation_atom():
    delegation_atom = atom_for_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    violation_atom = atom_for_violation(_DELEGATEE, _NORM_ID)
    _, revoke_rule, _ = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    assert revoke_rule.body == frozenset({delegation_atom, violation_atom})


def test_revoke_is_not_obligatory_without_the_violation_atom():
    delegation_atom = atom_for_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    _, revoke_rule, _ = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    (revoke_atom,) = revoke_rule.head
    given = frozenset({delegation_atom})
    assert is_obligatory(frozenset({revoke_atom}), given, [revoke_rule]) is False


def test_revoke_is_obligatory_with_both_delegation_and_violation_atoms():
    delegation_atom = atom_for_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    violation_atom = atom_for_violation(_DELEGATEE, _NORM_ID)
    _, revoke_rule, _ = ground_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    (revoke_atom,) = revoke_rule.head
    given = frozenset({delegation_atom, violation_atom})
    assert is_obligatory(frozenset({revoke_atom}), given, [revoke_rule]) is True


def test_ground_delegation_weight_override():
    audit_rule, revoke_rule, liable_rule = ground_delegation(
        _DELEGATOR, _DELEGATEE, _NORM_ID, weight=42.0
    )
    assert audit_rule.weight == revoke_rule.weight == liable_rule.weight == 42.0
