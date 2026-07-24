from datetime import datetime, timedelta

from deontic_reasoner.models import Norm, Relation
from deontic_reasoner.scope import scope_matches

_T0 = datetime(2026, 1, 1, 0, 0, 0)


def _norm(**overrides) -> Norm:
    fields = {
        "id": "n1",
        "relation": Relation.PRIVILEGE,
        "subject": "Agent",
        "action": "read",
        "resource": "/x",
    }
    fields.update(overrides)
    return Norm(**fields)


def test_fully_default_norm_is_in_scope_for_any_now_and_empty_registry():
    norm = _norm()
    assert scope_matches(norm, {}, {}, now=_T0) is True
    assert scope_matches(norm, {}, {}, now=_T0 + timedelta(days=365)) is True


def test_now_before_valid_from_is_out_of_scope():
    norm = _norm(valid_from=_T0)
    assert scope_matches(norm, {}, {}, now=_T0 - timedelta(seconds=1)) is False


def test_now_equal_to_valid_from_is_in_scope():
    norm = _norm(valid_from=_T0)
    assert scope_matches(norm, {}, {}, now=_T0) is True


def test_now_after_valid_until_is_out_of_scope():
    norm = _norm(valid_until=_T0)
    assert scope_matches(norm, {}, {}, now=_T0 + timedelta(seconds=1)) is False


def test_now_equal_to_valid_until_is_in_scope():
    norm = _norm(valid_until=_T0)
    assert scope_matches(norm, {}, {}, now=_T0) is True


def test_in_temporal_window_but_condition_fails_is_out_of_scope():
    norm = _norm(valid_until=_T0 + timedelta(hours=24), condition="always_false")
    registry = {"always_false": lambda n, request: False}
    assert scope_matches(norm, {}, registry, now=_T0 + timedelta(hours=1)) is False


def test_condition_passes_but_outside_temporal_window_is_out_of_scope():
    norm = _norm(valid_until=_T0 + timedelta(hours=24), condition="always_true")
    registry = {"always_true": lambda n, request: True}
    assert scope_matches(norm, {}, registry, now=_T0 + timedelta(hours=25)) is False


def test_both_temporal_and_condition_pass_is_in_scope():
    norm = _norm(valid_until=_T0 + timedelta(hours=24), condition="always_true")
    registry = {"always_true": lambda n, request: True}
    assert scope_matches(norm, {}, registry, now=_T0 + timedelta(hours=1)) is True


def test_section_14_1_regression_same_norm_different_now_gives_different_results():
    norm = _norm(valid_until=_T0 + timedelta(hours=24))
    assert scope_matches(norm, {}, {}, now=_T0 + timedelta(hours=1)) is True
    assert scope_matches(norm, {}, {}, now=_T0 + timedelta(hours=25)) is False
