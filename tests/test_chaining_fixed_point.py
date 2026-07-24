import pytest

from deontic_reasoner.chaining import ForwardChainTimeout, forward_chain
from deontic_reasoner.delegation import exercise_power
from deontic_reasoner.models import Norm, Relation


def test_chain_result_has_expected_field_types():
    result = forward_chain(norms={})
    assert isinstance(result.norms, dict)
    assert isinstance(result.facts, frozenset)
    assert isinstance(result.rules, tuple)
    assert isinstance(result.iterations, int)


def test_trivial_call_still_runs_the_grounding_step():
    power_norm = Norm(id="p0", relation=Relation.POWER, subject="A", action="grant", resource="res0")
    result = forward_chain(norms={"p0": power_norm})
    assert result.iterations == 1
    assert "p0" in result.norms
    assert len(result.facts) == 1


def test_dangling_power_norm_id_contributes_nothing_without_error():
    kwargs = {"subject": "X", "relation": Relation.PRIVILEGE, "action": "read", "resource": "R"}
    result = forward_chain(norms={}, power_exercises=(("missing", kwargs),))
    assert result.norms == {}
    assert result.iterations == 1


def test_forward_chain_is_deterministic_across_repeated_calls():
    power_norm = Norm(
        id="p1", relation=Relation.POWER, subject="A", action="grant", resource="res", counterparty="B"
    )
    kwargs = {"subject": "B", "relation": Relation.PRIVILEGE, "action": "read", "resource": "R"}
    power_exercises = (("p1", kwargs),)
    first = forward_chain(norms={"p1": power_norm}, power_exercises=power_exercises)
    second = forward_chain(norms={"p1": power_norm}, power_exercises=power_exercises)
    assert first == second


def test_forward_chain_raises_timeout_when_max_iterations_exhausted_mid_growth():
    p0 = Norm(id="p0", relation=Relation.POWER, subject="A", action="grant", resource="res0")
    kwargs1 = {"subject": "B", "relation": Relation.POWER, "action": "grant", "resource": "res1"}
    n1_preview = exercise_power(p0, **kwargs1)
    kwargs2 = {"subject": "C", "relation": Relation.PRIVILEGE, "action": "read", "resource": "res2"}
    power_exercises = (("p0", kwargs1), (n1_preview.id, kwargs2))
    with pytest.raises(ForwardChainTimeout):
        forward_chain(norms={"p0": p0}, power_exercises=power_exercises, max_iterations=1)
