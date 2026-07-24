from datetime import datetime, timedelta

from deontic_reasoner.delegation import delegate_with_narrowing
from deontic_reasoner.models import Norm, Relation

_T0 = datetime(2026, 1, 1, 0, 0, 0)

_PARENT = Norm(
    id="p1",
    relation=Relation.PRIVILEGE,
    subject="AnalyticsAgent",
    action="read",
    resource="/data/analytics/**",
    valid_from=_T0,
    valid_until=_T0 + timedelta(hours=24),
)


def test_relation_action_resource_carry_over_from_parent_unchanged():
    granted = delegate_with_narrowing(_PARENT, subject="VisualizationAgent")
    assert granted.relation == _PARENT.relation
    assert granted.action == _PARENT.action
    assert granted.resource == _PARENT.resource
    assert granted.subject == "VisualizationAgent"


def test_wider_candidate_window_is_narrowed_to_parents_window():
    granted = delegate_with_narrowing(
        _PARENT,
        subject="VisualizationAgent",
        valid_from=_T0 - timedelta(hours=1),
        valid_until=_T0 + timedelta(hours=48),
    )
    assert granted.valid_from == _T0
    assert granted.valid_until == _T0 + timedelta(hours=24)


def test_narrower_candidate_window_passes_through_unchanged():
    candidate_from = _T0 + timedelta(hours=1)
    candidate_until = _T0 + timedelta(hours=2)
    granted = delegate_with_narrowing(
        _PARENT,
        subject="VisualizationAgent",
        valid_from=candidate_from,
        valid_until=candidate_until,
    )
    assert granted.valid_from == candidate_from
    assert granted.valid_until == candidate_until


def test_none_candidate_bounds_never_widen_parents_window():
    granted = delegate_with_narrowing(_PARENT, subject="VisualizationAgent")
    assert granted.valid_from == _PARENT.valid_from
    assert granted.valid_until == _PARENT.valid_until


def test_id_is_deterministic_given_identical_arguments():
    first = delegate_with_narrowing(_PARENT, subject="VisualizationAgent")
    second = delegate_with_narrowing(_PARENT, subject="VisualizationAgent")
    assert first.id == second.id
    assert first == second
