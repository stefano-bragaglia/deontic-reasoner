from deontic_reasoner.models import HardConstraint, Rule, World
from deontic_reasoner.preference import excludes, violates


def test_violates_true_when_body_satisfied_and_head_not():
    rule = Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=1.0)
    assert violates(rule, World({"delegated"})) is True


def test_violates_false_when_body_and_head_satisfied():
    rule = Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=1.0)
    assert violates(rule, World({"delegated", "audit"})) is False


def test_violates_empty_body_is_violated_iff_head_unsatisfied():
    rule = Rule(body=frozenset(), head=frozenset({"logged"}), weight=1.0)
    assert violates(rule, World()) is True
    assert violates(rule, World({"logged"})) is False


def test_violates_empty_head_is_never_violated():
    rule = Rule(body=frozenset({"delegated"}), head=frozenset(), weight=1.0)
    assert violates(rule, World({"delegated"})) is False
    assert violates(rule, World()) is False


def test_violates_false_when_body_unsatisfied_regardless_of_head():
    rule = Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=1.0)
    assert violates(rule, World()) is False
    assert violates(rule, World({"audit"})) is False


def test_excludes_true_when_all_forbidden_atoms_present():
    constraint = HardConstraint(forbidden=frozenset({"sent", "blocked"}))
    assert excludes(constraint, World({"sent", "blocked"})) is True
    assert excludes(constraint, World({"sent", "blocked", "extra"})) is True


def test_excludes_false_when_not_all_forbidden_atoms_present():
    constraint = HardConstraint(forbidden=frozenset({"sent", "blocked"}))
    assert excludes(constraint, World({"sent"})) is False
    assert excludes(constraint, World()) is False


def test_excludes_empty_forbidden_never_excludes():
    constraint = HardConstraint(forbidden=frozenset())
    assert excludes(constraint, World()) is False
    assert excludes(constraint, World({"anything"})) is False
