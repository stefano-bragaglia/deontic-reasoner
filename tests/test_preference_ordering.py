from deontic_reasoner.models import Rule, World
from deontic_reasoner.preference import PreferenceCriterion, preferred, violated_rules


def test_preference_criterion_members():
    assert {
        PreferenceCriterion.SUBSET,
        PreferenceCriterion.COUNT,
        PreferenceCriterion.WEIGHTED_COUNT,
    } == set(PreferenceCriterion)


def test_violated_rules_returns_exactly_the_violated_subset():
    rule_ok = Rule(body=frozenset(), head=frozenset({"logged"}), weight=1.0)
    rule_violated = Rule(body=frozenset(), head=frozenset({"audited"}), weight=1.0)
    world = World({"logged"})
    assert violated_rules(world, [rule_ok, rule_violated]) == frozenset({rule_violated})


def test_subset_criterion_prefers_strict_subset_of_violations():
    rule1 = Rule(body=frozenset(), head=frozenset({"x"}), weight=1.0)
    rule2 = Rule(body=frozenset(), head=frozenset({"y"}), weight=1.0)
    rules = [rule1, rule2]
    world_violates_both = World()
    world_violates_one = World({"x"})
    assert preferred(world_violates_one, world_violates_both, rules, PreferenceCriterion.SUBSET) is True
    assert preferred(world_violates_both, world_violates_one, rules, PreferenceCriterion.SUBSET) is False


def test_subset_criterion_reports_incomparable_worlds():
    rule1 = Rule(body=frozenset(), head=frozenset({"x"}), weight=1.0)
    rule2 = Rule(body=frozenset(), head=frozenset({"y"}), weight=1.0)
    rules = [rule1, rule2]
    world_a = World({"y"})
    world_b = World({"x"})
    assert preferred(world_a, world_b, rules, PreferenceCriterion.SUBSET) is False
    assert preferred(world_b, world_a, rules, PreferenceCriterion.SUBSET) is False


def test_count_criterion_prefers_fewer_violations():
    rule1 = Rule(body=frozenset(), head=frozenset({"x"}), weight=1.0)
    rule2 = Rule(body=frozenset(), head=frozenset({"y"}), weight=1.0)
    rules = [rule1, rule2]
    world_zero = World({"x", "y"})
    world_one = World({"x"})
    assert preferred(world_zero, world_one, rules, PreferenceCriterion.COUNT) is True
    assert preferred(world_one, world_zero, rules, PreferenceCriterion.COUNT) is False


def test_count_criterion_is_always_comparable():
    rule1 = Rule(body=frozenset(), head=frozenset({"x"}), weight=1.0)
    rule2 = Rule(body=frozenset(), head=frozenset({"y"}), weight=1.0)
    rules = [rule1, rule2]
    world_a = World({"y"})
    world_b = World({"x"})
    assert preferred(world_a, world_b, rules, PreferenceCriterion.COUNT) is True
    assert preferred(world_b, world_a, rules, PreferenceCriterion.COUNT) is True


def test_weighted_count_prefers_lower_total_violated_weight():
    rule_light = Rule(body=frozenset(), head=frozenset({"x"}), weight=1.0)
    rule_heavy = Rule(body=frozenset(), head=frozenset({"y"}), weight=10.0)
    rules = [rule_light, rule_heavy]
    world_violates_light = World({"y"})
    world_violates_heavy = World({"x"})
    assert (
        preferred(world_violates_light, world_violates_heavy, rules, PreferenceCriterion.WEIGHTED_COUNT)
        is True
    )
    assert (
        preferred(world_violates_heavy, world_violates_light, rules, PreferenceCriterion.WEIGHTED_COUNT)
        is False
    )


def test_weighted_count_is_the_default_criterion():
    rule_light = Rule(body=frozenset(), head=frozenset({"x"}), weight=1.0)
    rule_heavy = Rule(body=frozenset(), head=frozenset({"y"}), weight=10.0)
    rules = [rule_light, rule_heavy]
    world_violates_light = World({"y"})
    world_violates_heavy = World({"x"})
    assert preferred(world_violates_light, world_violates_heavy, rules) is True


def test_weighted_count_result_independent_of_rules_list_order():
    rule_a = Rule(body=frozenset(), head=frozenset({"a_atom"}), weight=3.0)
    rule_b = Rule(body=frozenset(), head=frozenset({"b_atom"}), weight=5.0)
    rule_c = Rule(body=frozenset(), head=frozenset({"c_atom"}), weight=7.0)
    world_x = World()
    world_y = World({"a_atom"})
    rules_forward = [rule_a, rule_b, rule_c]
    rules_reversed = [rule_c, rule_b, rule_a]
    assert preferred(world_x, world_y, rules_forward, PreferenceCriterion.WEIGHTED_COUNT) == preferred(
        world_x, world_y, rules_reversed, PreferenceCriterion.WEIGHTED_COUNT
    )


def test_empty_rules_makes_every_world_equally_preferred():
    world_a = World({"anything"})
    world_b = World()
    for criterion in PreferenceCriterion:
        assert preferred(world_a, world_b, [], criterion) is True
        assert preferred(world_b, world_a, [], criterion) is True
