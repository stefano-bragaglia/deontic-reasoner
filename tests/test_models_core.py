import dataclasses

import pytest

from deontic_reasoner.models import Atom, HardConstraint, Rule, World


def test_atom_is_str():
    assert Atom("x") == "x"
    assert isinstance(Atom("x"), str)


def test_world_is_hashable_frozenset_supporting_set_ops():
    world = World({"a", "b"})
    assert isinstance(world, frozenset)
    hash(world)
    assert world & World({"b", "c"}) == frozenset({"b"})
    assert world | World({"c"}) == frozenset({"a", "b", "c"})
    assert World({"a"}) <= world


def test_rule_fields_and_defaults():
    rule = Rule(head=frozenset({"audit"}), weight=10.0)
    assert rule.body == frozenset()
    assert rule.head == frozenset({"audit"})
    assert rule.weight == 10.0


def test_rule_explicit_body_conjunction():
    rule = Rule(body=frozenset({"delegated", "authorized"}), head=frozenset({"audit"}), weight=1.0)
    assert rule.body == frozenset({"delegated", "authorized"})


def test_two_rules_same_body_head_different_weight_are_not_equal():
    r1 = Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=10.0)
    r2 = Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=5.0)
    assert r1 != r2


def test_hard_constraint_fields():
    constraint = HardConstraint(forbidden=frozenset({"sent", "blocked"}))
    assert constraint.forbidden == frozenset({"sent", "blocked"})


def test_rule_is_hashable_and_frozen():
    rule = Rule(body=frozenset({"a"}), head=frozenset({"b"}), weight=1.0)
    hash(rule)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rule.weight = 2.0


def test_hard_constraint_is_hashable_and_frozen():
    constraint = HardConstraint(forbidden=frozenset({"a"}))
    hash(constraint)
    with pytest.raises(dataclasses.FrozenInstanceError):
        constraint.forbidden = frozenset({"b"})


def test_rule_equality_independent_of_keyword_order():
    r1 = Rule(body=frozenset({"a"}), head=frozenset({"b"}), weight=1.0)
    r2 = Rule(weight=1.0, head=frozenset({"b"}), body=frozenset({"a"}))
    assert r1 == r2
    assert hash(r1) == hash(r2)


def test_hard_constraint_equality_independent_of_construction_order():
    hc1 = HardConstraint(forbidden=frozenset({"a", "b"}))
    hc2 = HardConstraint(forbidden=frozenset({"b", "a"}))
    assert hc1 == hc2
    assert hash(hc1) == hash(hc2)
