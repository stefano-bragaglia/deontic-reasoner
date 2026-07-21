import dataclasses
from datetime import datetime, timedelta

import pytest

from deontic_reasoner.models import Norm, Relation


def test_relation_members():
    assert {Relation.PRIVILEGE, Relation.RIGHT, Relation.POWER, Relation.IMMUNITY} == set(Relation)


def test_norm_required_fields_and_defaults():
    norm = Norm(
        id="n1",
        relation=Relation.PRIVILEGE,
        subject="DataAgent",
        action="read",
        resource="/data/analytics/**",
    )
    assert norm.id == "n1"
    assert norm.relation == Relation.PRIVILEGE
    assert norm.subject == "DataAgent"
    assert norm.action == "read"
    assert norm.resource == "/data/analytics/**"
    assert norm.counterparty is None
    assert norm.valid_from is None
    assert norm.valid_until is None
    assert norm.condition is None


def test_norm_directed_relation_with_counterparty():
    norm = Norm(
        id="n2",
        relation=Relation.RIGHT,
        subject="FileAgent",
        action="write",
        resource="/out/report.csv",
        counterparty="filesystem",
    )
    assert norm.counterparty == "filesystem"


def test_norm_temporal_bounds_and_condition():
    t0 = datetime(2026, 1, 1)
    norm = Norm(
        id="n3",
        relation=Relation.PRIVILEGE,
        subject="DataAgent",
        action="read",
        resource="/data/analytics/**",
        valid_from=t0,
        valid_until=t0 + timedelta(hours=24),
        condition="business_hours",
    )
    assert norm.valid_from == t0
    assert norm.valid_until == t0 + timedelta(hours=24)
    assert norm.condition == "business_hours"


def test_norm_is_hashable_and_frozen():
    norm = Norm(
        id="n1",
        relation=Relation.PRIVILEGE,
        subject="DataAgent",
        action="read",
        resource="/data/analytics/**",
    )
    hash(norm)
    with pytest.raises(dataclasses.FrozenInstanceError):
        norm.subject = "OtherAgent"


def test_norm_equality_and_hash_for_identical_field_values():
    n1 = Norm(
        id="n1",
        relation=Relation.RIGHT,
        subject="FileAgent",
        action="write",
        resource="/out/report.csv",
        counterparty="filesystem",
    )
    n2 = Norm(
        counterparty="filesystem",
        id="n1",
        relation=Relation.RIGHT,
        subject="FileAgent",
        action="write",
        resource="/out/report.csv",
    )
    assert n1 == n2
    assert hash(n1) == hash(n2)
