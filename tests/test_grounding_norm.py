from dataclasses import replace

from deontic_reasoner.grounding import CORRELATIVE_WEIGHT, atom_for_norm, ground_norm
from deontic_reasoner.models import Norm, Relation

_RIGHT = Norm(
    id="n1",
    relation=Relation.RIGHT,
    subject="FileAgent",
    action="write",
    resource="/out/report.csv",
    counterparty="filesystem",
)


def test_atom_for_norm_is_deterministic():
    assert atom_for_norm(_RIGHT) == atom_for_norm(_RIGHT)
    same_norm = replace(_RIGHT)
    assert atom_for_norm(_RIGHT) == atom_for_norm(same_norm)


def test_ground_norm_right_with_counterparty_produces_duty_rule():
    atom, rule = ground_norm(_RIGHT)
    assert atom == atom_for_norm(_RIGHT)
    assert rule is not None
    assert rule.body == frozenset({atom})
    assert len(rule.head) == 1
    (head_atom,) = rule.head
    assert "filesystem" in head_atom
    assert "write" in head_atom
    assert "/out/report.csv" in head_atom
    assert _RIGHT.subject not in head_atom


def test_ground_norm_power_with_counterparty_produces_liability_rule():
    norm = replace(_RIGHT, relation=Relation.POWER)
    _, rule = ground_norm(norm)
    assert rule is not None
    (head_atom,) = rule.head
    assert "liability" in head_atom


def test_ground_norm_immunity_with_counterparty_produces_disability_rule():
    norm = replace(_RIGHT, relation=Relation.IMMUNITY)
    _, rule = ground_norm(norm)
    assert rule is not None
    (head_atom,) = rule.head
    assert "disability" in head_atom


def test_ground_norm_right_produces_duty_labelled_atom():
    _, rule = ground_norm(_RIGHT)
    assert rule is not None
    (head_atom,) = rule.head
    assert "duty" in head_atom


def test_ground_norm_privilege_returns_no_rule_regardless_of_counterparty():
    norm = replace(_RIGHT, relation=Relation.PRIVILEGE)
    atom, rule = ground_norm(norm)
    assert atom == atom_for_norm(norm)
    assert rule is None


def test_ground_norm_right_without_counterparty_returns_no_rule():
    norm = replace(_RIGHT, counterparty=None)
    atom, rule = ground_norm(norm)
    assert atom == atom_for_norm(norm)
    assert rule is None


def test_ground_norm_power_without_counterparty_returns_no_rule():
    norm = replace(_RIGHT, relation=Relation.POWER, counterparty=None)
    _, rule = ground_norm(norm)
    assert rule is None


def test_ground_norm_immunity_without_counterparty_returns_no_rule():
    norm = replace(_RIGHT, relation=Relation.IMMUNITY, counterparty=None)
    _, rule = ground_norm(norm)
    assert rule is None


def test_different_counterparties_produce_different_correlative_atoms():
    other = replace(_RIGHT, id="n2", counterparty="database")
    _, rule_a = ground_norm(_RIGHT)
    _, rule_b = ground_norm(other)
    assert rule_a is not None
    assert rule_b is not None
    assert rule_a.head != rule_b.head


def test_ground_norm_default_weight_is_correlative_weight():
    _, rule = ground_norm(_RIGHT)
    assert rule is not None
    assert rule.weight == CORRELATIVE_WEIGHT


def test_ground_norm_weight_override():
    _, rule = ground_norm(_RIGHT, weight=42.0)
    assert rule is not None
    assert rule.weight == 42.0
