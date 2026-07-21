import json
from datetime import datetime, timedelta

from deontic_reasoner.models import HardConstraint, Norm, Relation, Rule, World
from deontic_reasoner.serialization import from_dict, to_dict, world_from_list, world_to_list


def test_rule_round_trip_all_defaults():
    rule = Rule(head=frozenset({"audit"}), weight=1.0)
    assert from_dict(Rule, to_dict(rule)) == rule


def test_rule_round_trip_fully_populated():
    rule = Rule(head=frozenset({"audit", "logged"}), weight=10.0, body=frozenset({"delegated"}))
    assert from_dict(Rule, to_dict(rule)) == rule


def test_rule_to_dict_is_json_serializable():
    rule = Rule(head=frozenset({"audit"}), weight=1.0, body=frozenset({"delegated"}))
    assert json.loads(json.dumps(to_dict(rule))) is not None


def test_rule_body_and_head_round_trip_through_json_array_to_frozenset():
    rule = Rule(head=frozenset({"audit", "logged"}), weight=1.0, body=frozenset({"a", "b"}))
    data = to_dict(rule)
    assert isinstance(data["body"], list)
    assert isinstance(data["head"], list)
    restored = from_dict(Rule, data)
    assert restored.body == frozenset({"a", "b"})
    assert restored.head == frozenset({"audit", "logged"})


def test_hard_constraint_round_trip_empty():
    constraint = HardConstraint(forbidden=frozenset())
    assert from_dict(HardConstraint, to_dict(constraint)) == constraint


def test_hard_constraint_round_trip_non_empty():
    constraint = HardConstraint(forbidden=frozenset({"sent", "blocked"}))
    assert from_dict(HardConstraint, to_dict(constraint)) == constraint


def test_hard_constraint_to_dict_is_json_serializable():
    constraint = HardConstraint(forbidden=frozenset({"a"}))
    assert json.loads(json.dumps(to_dict(constraint))) is not None


def test_norm_round_trip_all_defaults():
    norm = Norm(id="n1", relation=Relation.PRIVILEGE, subject="DataAgent", action="read", resource="/data/**")
    assert from_dict(Norm, to_dict(norm)) == norm


def test_norm_round_trip_fully_populated():
    t0 = datetime(2026, 1, 1)
    norm = Norm(
        id="n2",
        relation=Relation.RIGHT,
        subject="FileAgent",
        action="write",
        resource="/out/report.csv",
        counterparty="filesystem",
        valid_from=t0,
        valid_until=t0 + timedelta(hours=24),
        condition="business_hours",
    )
    assert from_dict(Norm, to_dict(norm)) == norm


def test_norm_to_dict_is_json_serializable():
    norm = Norm(id="n1", relation=Relation.PRIVILEGE, subject="DataAgent", action="read", resource="/data/**")
    assert json.loads(json.dumps(to_dict(norm))) is not None


def test_norm_none_optional_fields_round_trip_as_none():
    norm = Norm(id="n1", relation=Relation.PRIVILEGE, subject="DataAgent", action="read", resource="/data/**")
    data = to_dict(norm)
    assert data["counterparty"] is None
    assert data["valid_from"] is None
    assert data["valid_until"] is None
    assert data["condition"] is None
    restored = from_dict(Norm, data)
    assert restored.counterparty is None
    assert restored.valid_from is None
    assert restored.valid_until is None
    assert restored.condition is None


def test_norm_datetime_fields_round_trip_via_isoformat():
    t0 = datetime(2026, 1, 1, 12, 30)
    norm = Norm(
        id="n1", relation=Relation.PRIVILEGE, subject="DataAgent", action="read", resource="/data/**", valid_from=t0
    )
    data = to_dict(norm)
    assert data["valid_from"] == t0.isoformat()
    restored = from_dict(Norm, data)
    assert restored.valid_from == t0


def test_norm_relation_round_trips_via_value_string():
    norm = Norm(id="n1", relation=Relation.RIGHT, subject="FileAgent", action="write", resource="/out/report.csv")
    data = to_dict(norm)
    assert data["relation"] == "right"
    restored = from_dict(Norm, data)
    assert restored.relation == Relation.RIGHT


def test_world_round_trip_empty():
    world: World = frozenset()
    assert world_from_list(world_to_list(world)) == world


def test_world_round_trip_non_empty():
    world: World = frozenset({"a", "b", "c"})
    assert world_from_list(world_to_list(world)) == world
