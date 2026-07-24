from deontic_reasoner.models import HardConstraint, Rule, World
from deontic_reasoner.preference import best_worlds


def test_every_returned_world_satisfies_antecedent():
    antecedent = frozenset({"delegated"})
    rules = [Rule(body=frozenset(), head=frozenset({"audit"}), weight=1.0)]
    worlds = best_worlds(antecedent, rules)
    assert len(worlds) > 0
    for world in worlds:
        assert antecedent <= world


def test_enumeration_scoped_to_antecedent_and_rule_atoms():
    antecedent = frozenset({"delegated"})
    rules = [Rule(body=frozenset({"delegated"}), head=frozenset({"audit"}), weight=1.0)]
    relevant_atoms = frozenset({"delegated", "audit"})
    worlds = best_worlds(antecedent, rules)
    for world in worlds:
        assert world <= relevant_atoms


def test_hard_constraint_excludes_world_even_if_otherwise_best():
    rules = [Rule(body=frozenset(), head=frozenset({"sent"}), weight=1.0)]
    worlds_no_constraint = best_worlds(frozenset(), rules)
    assert World({"sent"}) in worlds_no_constraint

    constraint = HardConstraint(forbidden=frozenset({"sent"}))
    worlds_with_constraint = best_worlds(frozenset(), rules, hard_constraints=[constraint])
    assert World({"sent"}) not in worlds_with_constraint


def test_ties_return_all_most_preferred_worlds():
    rules = [Rule(body=frozenset(), head=frozenset({"x"}), weight=0.0)]
    worlds = best_worlds(frozenset(), rules)
    assert worlds == {World(), World({"x"})}


def test_empty_result_when_all_antecedent_satisfying_worlds_excluded():
    antecedent = frozenset({"x"})
    constraint = HardConstraint(forbidden=frozenset({"x"}))
    worlds = best_worlds(antecedent, [], hard_constraints=[constraint])
    assert worlds == set()


def test_default_criterion_is_weighted_count():
    rule_a = Rule(head=frozenset({"a"}), weight=1.0)
    rule_b = Rule(head=frozenset({"b"}), weight=1.0)
    rule_c = Rule(head=frozenset({"c"}), weight=10.0)
    rules = [rule_a, rule_b, rule_c]
    constraint = HardConstraint(forbidden=frozenset({"a", "b", "c"}))
    worlds = best_worlds(frozenset(), rules, hard_constraints=[constraint])
    assert worlds == {World({"a", "c"}), World({"b", "c"})}
