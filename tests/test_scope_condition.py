import pytest

from deontic_reasoner.models import Norm, Relation
from deontic_reasoner.scope import UnknownPredicateError, evaluate_condition

_NORM = Norm(id="n1", relation=Relation.PRIVILEGE, subject="Agent", action="read", resource="/x")


def _norm_with_condition(condition: str) -> Norm:
    return Norm(
        id="n1",
        relation=Relation.PRIVILEGE,
        subject="Agent",
        action="read",
        resource="/x",
        condition=condition,
    )


def test_none_condition_returns_true_without_consulting_registry():
    def _explode(norm, request):
        raise AssertionError("registry must not be consulted when condition is None")

    registry = {"business_hours": _explode}
    assert evaluate_condition(_NORM, {}, registry) is True


def test_registered_condition_returns_the_callables_result():
    norm = _norm_with_condition("business_hours")
    registry = {"business_hours": lambda n, request: 9 <= request["hour"] < 17}
    assert evaluate_condition(norm, {"hour": 10}, registry) is True
    assert evaluate_condition(norm, {"hour": 20}, registry) is False


def test_registered_condition_receives_norm_and_request():
    received = {}

    def _record(norm, request):
        received["norm"] = norm
        received["request"] = request
        return True

    norm = _norm_with_condition("record")
    registry = {"record": _record}
    evaluate_condition(norm, {"hour": 1}, registry)
    assert received["norm"] is norm
    assert received["request"] == {"hour": 1}


def test_unregistered_condition_raises_unknown_predicate_error():
    norm = _norm_with_condition("not_registered")
    with pytest.raises(UnknownPredicateError):
        evaluate_condition(norm, {}, {})


def test_python_syntax_condition_name_is_never_executed():
    side_effects = []
    norm = _norm_with_condition("__import__('os').system('echo pwned')")
    registry = {"harmless": lambda n, request: side_effects.append("called") or True}
    with pytest.raises(UnknownPredicateError):
        evaluate_condition(norm, {}, registry)
    assert side_effects == []
