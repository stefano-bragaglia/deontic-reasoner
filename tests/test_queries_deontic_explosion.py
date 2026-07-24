from deontic_reasoner.models import Rule
from deontic_reasoner.queries import is_obligatory

# §14.9 adaptation: WEIGHTED_COUNT's total violated weight is additive across atom-disjoint
# rule groups, so a conflicting pair over task1/not_task1 can never leak into an unrelated
# query over task2 — this is structural (disjoint atoms), not the result of any explicit
# subject/resource-scoping mechanism (there is none in this API).
_UNRELATED = Rule(body=frozenset(), head=frozenset({"task2"}), weight=4.0)
_GIVEN = frozenset()
_B = frozenset({"task2"})


def test_unrelated_obligation_holds_despite_conflicting_pair_elsewhere():
    conflicting_pair = [
        Rule(body=frozenset(), head=frozenset({"task1"}), weight=3.0),
        Rule(body=frozenset(), head=frozenset({"not_task1"}), weight=7.0),
    ]
    rules = [*conflicting_pair, _UNRELATED]
    assert is_obligatory(_B, _GIVEN, rules) is True


def test_unrelated_obligation_is_unchanged_when_conflicting_pair_weights_are_swapped():
    conflicting_pair = [
        Rule(body=frozenset(), head=frozenset({"task1"}), weight=7.0),
        Rule(body=frozenset(), head=frozenset({"not_task1"}), weight=3.0),
    ]
    rules = [*conflicting_pair, _UNRELATED]
    assert is_obligatory(_B, _GIVEN, rules) is True
