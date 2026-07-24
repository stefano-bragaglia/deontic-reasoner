from deontic_reasoner.models import HardConstraint, Rule
from deontic_reasoner.queries import is_obligatory, is_permitted


def test_is_obligatory_true_when_b_holds_in_every_best_world():
    rules = [Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=10.0)]
    assert is_obligatory(frozenset({"audit"}), frozenset({"delegated"}), rules) is True


def test_is_obligatory_false_when_b_does_not_hold_in_every_best_world():
    assert is_obligatory(frozenset({"audit"}), frozenset(), []) is False


def test_is_permitted_true_when_b_holds_in_some_best_world():
    rules = [Rule(body=frozenset(), head=frozenset({"x"}), weight=0.0)]
    assert is_permitted(frozenset({"x"}), frozenset(), rules) is True


def test_is_permitted_false_when_b_holds_in_no_best_world():
    rules = [Rule(body=frozenset(), head=frozenset({"audit"}), weight=10.0)]
    assert is_permitted(frozenset({"never_true"}), frozenset(), rules) is False


def test_vacuous_case_empty_best_worlds():
    hard_constraints = [HardConstraint(forbidden=frozenset({"x"}))]
    given = frozenset({"x"})
    assert is_obligatory(frozenset({"anything"}), given, [], hard_constraints=hard_constraints) is True
    assert is_permitted(frozenset({"anything"}), given, [], hard_constraints=hard_constraints) is False


def test_empty_b_is_obligatory_whenever_best_worlds_nonempty():
    assert is_obligatory(frozenset(), frozenset(), []) is True


def test_default_criterion_is_weighted_count():
    rule_a = Rule(head=frozenset({"a"}), weight=1.0)
    rule_b = Rule(head=frozenset({"b"}), weight=1.0)
    rule_c = Rule(head=frozenset({"c"}), weight=10.0)
    rules = [rule_a, rule_b, rule_c]
    constraint = HardConstraint(forbidden=frozenset({"a", "b", "c"}))
    assert is_obligatory(frozenset({"c"}), frozenset(), rules, hard_constraints=[constraint]) is True


def test_queries_are_deterministic_across_repeated_calls():
    rules = [Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=10.0)]
    obligatory_results = {
        is_obligatory(frozenset({"audit"}), frozenset({"delegated"}), rules) for _ in range(5)
    }
    permitted_results = {
        is_permitted(frozenset({"audit"}), frozenset({"delegated"}), rules) for _ in range(5)
    }
    assert obligatory_results == {True}
    assert permitted_results == {True}
